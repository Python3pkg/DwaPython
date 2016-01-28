# Copyright (C) 2014 Adam Schubert <adam.schubert@sg1-game.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import json
import sys
import dwa.DwaException as DwaException

is_python_3 = sys.version_info >= (3, 0)

if is_python_3:
    import http.client as httplib
    from urllib.parse import urljoin
    from urllib.parse import urlencode
    from urllib.parse import urlparse
else:
    import httplib
    from urlparse import urljoin
    from urllib import urlencode
    from urlparse import urlparse


__author__ = "Adam Schubert <adam.schubert@sg1-game.net>"
__date__ = "$6.10.2014 5:09:42$"


class Requester:
    http_connection_class = httplib.HTTPConnection
    https_connection_class = httplib.HTTPSConnection

    @classmethod
    def inject_connection_classes(cls, http_connection_class, https_connection_class):
        cls.http_connection_class = http_connection_class
        cls.https_connection_class = https_connection_class

    @classmethod
    def reset_connection_classes(cls):
        cls.http_connection_class = httplib.HTTPConnection
        cls.https_connection_class = httplib.HTTPSConnection

    def __init__(self, token, base_url, timeout, version, user_agent):
        self.token = token
        self.base_url = base_url
        base_url_parsed = urlparse(base_url)
        self.hostname = base_url_parsed.hostname
        self.port = base_url_parsed.port
        self.prefix = base_url_parsed.path

        self.scheme = base_url_parsed.scheme
        if base_url_parsed.scheme == "https":
            self.connection_class = self.https_connection_class
        elif base_url_parsed.scheme == "http":
            self.connection_class = self.http_connection_class
        else:
            raise DwaException("Unknown URL scheme")
        self.timeout = timeout
        self.version = version
        self.user_agent = user_agent

    def request_json_check(self, type, url, parameters=None, input=None):
        return self.check(*self.request_json(type, url, parameters, input))

    def check(self, status, response_headers, output):
        output = self.structured_from_json(output)
        if status >= 400:
            raise self.create_exception(status, response_headers, output)
        return response_headers, output

    def create_exception(self, status, headers, output):
        if status == 500:
            exp = DwaException.ServerErrorException
        elif status == 401:
            exp = DwaException.BadCredentialsException
        elif status == 404:
            exp = DwaException.UnknownObjectException
        else:
            exp = DwaException.BadRequestException
        return exp(status, output)

    def structured_from_json(self, data):
        if len(data) == 0:
            return None
        else:
            # if we got data in bytes in python2, decode it to unicode
            if is_python_3 and isinstance(data, bytes):
                data = data.decode("utf-8")
            try:
                return json.loads(data)
            except ValueError:
                return {'data': data}

    def request_json(self, request_type, url, parameters=None, request_input=None):
        def encode(request_input):
            return "application/json", json.dumps(request_input)

        return self.request_encode(request_type, url, parameters, {}, request_input, encode)

    def request_encode(self, request_type, url, parameters, request_headers, request_input, encode):
        if parameters is None:
            parameters = {}
        if request_headers is None:
            request_headers = {}

        request_headers["User-Agent"] = self.user_agent

        url = self.build_url(url, parameters)

        encoded_input = "null"
        if request_input is not None:
            request_headers["Content-Type"], encoded_input = encode(request_input)

        return self.request_raw(request_type, url, request_headers, encoded_input)

    def build_url(self, url, parameters):
        final = urljoin(self.base_url, str(self.version) + url + '/' + self.token)
        if (len(parameters) > 0):
            final += '?' + urlencode(parameters)
        return final

    def request_raw(self, request_type, url, request_headers, request_input):
        connection = self.create_connection()
        connection.request(
            request_type,
            url,
            request_input,
            request_headers
        )
        response = connection.getresponse()

        status = response.status
        response_headers = dict((k.lower(), v) for k, v in response.getheaders())
        output = response.read()

        connection.close()

        self.log(request_type, url, request_headers, request_input, status, response_headers, output)

        return status, response_headers, output

    def create_connection(self):
        kwds = {}
        if not is_python_3:
            kwds["strict"] = True
        kwds["timeout"] = self.timeout
        return self.connection_class(self.hostname, self.port, **kwds)

    def log(self, type, url, request_headers, input, status, response_headers, output):
        logger = logging.getLogger(__name__)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("%s %s://%s%s %s %s ==> %i %s %s", str(type), self.scheme, self.hostname, str(
                url), str(request_headers), str(input), status, str(response_headers), str(output))
