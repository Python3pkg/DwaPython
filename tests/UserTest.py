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

import tests.DwaTestCase as DwaTestCase
import unittest
import time

__author__ = "Adam Schubert <adam.schubert@sg1-game.net>"
__date__ = "$12.10.2014 2:20:45$"


class UserTest(DwaTestCase.DwaTestCase):

    def setUp(self):
        DwaTestCase.DwaTestCase.setUp(self)
        self.user = self.d.user()
        self.username = self.credential['username'] + 'UserTest' + str(time.time())

    def test_create(self):
        params = {}
        params['password'] = self.credential['password']
        params['username'] = self.username
        params['nickname'] = DwaTestCase.generate_nickname()
        params['email'] = self.username + '@divine-warfare.com'
        params['active'] = True
        # create
        message = self.user.create(params)['message']

        # delete
        user_data = self.user.token({'password': params['password'], 'username': params['username']})

        del_params = {}
        del_params['user_id'] = user_data['id']
        del_params['user_token'] = user_data['token']
        self.user.delete(del_params)

        self.assertEqual(message, 'User created')

    def test_delete(self):
        params = {}
        params['password'] = self.credential['password']
        params['username'] = self.username
        params['nickname'] = DwaTestCase.generate_nickname()
        params['email'] = self.username + '@divine-warfare.com'
        params['active'] = True

        # create
        self.user.create(params)
        user_data = self.user.token({'password': params['password'], 'username': params['username']})

        del_params = {}
        del_params['user_id'] = user_data['id']
        del_params['user_token'] = user_data['token']
        # delete
        message = self.user.delete(del_params)['message']
        self.assertEqual(message, 'User deleted')

    def test_list(self):
        data = self.user.list({'limit': 20, 'page': 0})
        self.assertEqual(data['message'], 'OK')
        self.assertIsNotNone(data['data'])
        self.assertIsNotNone(data['pages'])

    def test_token(self):
        data = self.user.token(self.credential)
        self.assertEqual(data['message'], 'Token created')
        self.assertEqual(len(data['token']), 32)
        self.assertIsNotNone(data['id'])
        self.assertRegexpMatches(data['token_expiration'], '(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})')

    def test_password(self):
        data_token = self.user.token(self.credential)
        data = self.user.password({'old_password': self.credential['password'], 'new_password': self.credential[
                                  'password'], 'user_token': data_token['token'], 'user_id': data_token['id']})
        self.assertEqual(data['message'], 'Password changed')

    def test_active(self):
        data_token = self.user.token(self.credential)
        data = self.user.active({'user_id': data_token['id'], 'active': True, 'user_token': data_token['token']})
        self.assertEqual(data['message'], 'User activated')

    def test_deactive(self):
        data_token = self.user.token(self.credential)
        data = self.user.active({'user_id': data_token['id'], 'active': False, 'user_token': data_token['token']})
        self.assertEqual(data['message'], 'User deactivated')

    def test_request_password_reset(self):
        email = self.credential['username'] + '@example.com'

        content_fill = 'abc' * 5333  # 16k of shit

        data = self.user.request_password_reset(
            {
                'email': email,
                'email_content': 'URL: example.com/password/reset/{reset_token}' + content_fill,
                'email_subject': 'Password reset unittest',
                'email_from': 'unittest@example.com'
            }
        )
        self.assertEqual(data['message'], 'Email not found')

    @unittest.expectedFailure
    def test_do_password_reset(self):
        # we use USER token as password reset token, cos we dont have reset token
        # (and we cant have it cos it is only in email) so this call will fail,
        # and that is a good thing :)
        data_token = self.user.token(self.credential)
        data = self.user.request_password_reset({'reset_token': data_token['token'], 'new_password': 'newPassword'})
        self.assertEqual(data['message'], 'Password changed')
