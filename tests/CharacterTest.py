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
import time

__author__ = "Adam Schubert <adam.schubert@sg1-game.net>"
__date__ = "$12.10.2014 4:08:10$"


class CharacterTest(DwaTestCase.DwaTestCase):

    def setUp(self):
        DwaTestCase.DwaTestCase.setUp(self)
        self.character = self.d.character()
        self.user_data = self.d.user().token(self.credential)

        # we must create one to get data of it
        create_params = {}
        create_params['user_token'] = self.user_data['token']
        create_params['server_id'] = 1
        create_params['user_id'] = self.user_data['id']
        create_params['faction_id'] = 1
        create_params['name'] = 'UnitTestCharacter ' + str(time.time())
        create_params['class'] = 1
        create_params['x'] = 0
        create_params['y'] = 0
        create_params['z'] = 0
        create_params['rotation'] = 0
        create_params['gender'] = 1
        create_params['max_health'] = 200
        create_params['max_mana'] = 100
        self.create_params = create_params
        self.createData = self.character.create(create_params)

    def test_list(self):
        list_params = {}
        list_params['server_id'] = 1
        # list_params['user_id'] = self.user_data['id']
        list_params['limit'] = 20
        list_params['page'] = 0

        list_data = self.character.list(list_params)
        self.assertEqual(list_data['message'], 'OK')

    def test_save(self):
        save_params = {}
        save_params['user_token'] = self.user_data['token']
        save_params['user_id'] = self.user_data['id']
        save_params['character_id'] = self.createData['id']
        save_params['x'] = 10
        save_params['y'] = 20
        save_params['z'] = 30
        save_params['health'] = 300
        save_params['mana'] = 200
        save_params['rotation'] = 0
        save_params['reputation'] = 200
        save_params['max_health'] = 500
        save_params['max_mana'] = 1000
        save_params['inventory'] = []

        save_data = self.character.save(save_params)
        self.assertEqual(save_data['message'], 'Character saved')

    def test_detail(self):
        detail_params = {}
        detail_params['user_token'] = self.user_data['token']
        detail_params['user_id'] = self.user_data['id']
        detail_params['character_id'] = self.createData['id']

        detail_data = self.character.detail(detail_params)
        self.assertEqual(detail_data['message'], 'OK')

    def test_create(self):
        create_params = {}
        create_params['user_token'] = self.user_data['token']
        create_params['server_id'] = 1
        create_params['user_id'] = self.user_data['id']
        create_params['faction_id'] = 1
        create_params['name'] = 'UnitTestCharacter ' + str(time.time())
        create_params['class'] = 1
        create_params['x'] = 0
        create_params['y'] = 0
        create_params['z'] = 0
        create_params['rotation'] = 0
        create_params['gender'] = 1
        create_params['max_health'] = 200
        create_params['max_mana'] = 100

        create_data = self.character.create(create_params)

        self.assertEqual(create_data['message'], 'Character created')
        self.assertIs(type(create_data['id']), int)

    def test_delete(self):
        delete_params = {}
        delete_params['user_token'] = self.user_data['token']
        delete_params['user_id'] = self.user_data['id']
        delete_params['character_id'] = self.createData['id']

        delete_data = self.character.delete(delete_params)

        self.assertEqual(delete_data['message'], 'Character deleted')
