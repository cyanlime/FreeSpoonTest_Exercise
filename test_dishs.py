import unittest
import requests
import json
import exceptions

class Test_Dishes_View(unittest.TestCase):
    def setUp(self):
        self.dishs_url = 'http://yijiayinong.com/api/business/dishs/'
        
    def test_fetch_dishes(self):
        dishes_response = requests.post(self.dishs_url)
        self.assertEqual(dishes_response.status_code, 200, msg = 'dishes response status code equals to 200.')
        try:
            dishes_response_content = json.loads(dishes_response.content)
            self.assertTrue(dishes_response_content, list, msg = 'dishes response content is a list.')
            self.assertLessEqual(len(dishes_response_content), 10, msg = 'dishes response content length no more than 10.')
            
            dishes_fields = ['url', 'id', 'name', 'user', 'desc', 'cover', 'status', 'tag', 'tips', 'create_time', 'steps',
                    'step_num', 'more', 'card_url']
            user_required_fields = ['id', 'name', 'create_time'] 
            user_optional_fields = ['wx_nickname', 'wx_headimgurl']
            steps_fields = ['image', 'plain', 'seq', 'create_time', 'width', 'height']
            more_fields = ['url', 'id', 'name', 'cover', 'create_time']

            for item in dishes_response_content:
                for field in dishes_fields:
                    self.assertIn(field, item, msg = 'dishes response content had field \'%s\'.' % field)

                for field2 in user_required_fields:
                    self.assertIn(field2, item, msg = 'user content had field \'%s\'.' % field2)
                
                for field3 in steps_fields:
                    self.assertIn(field3, item, msg = 'steps content had field \'%s\'.' % field3)
                self.assertEqual(len(item['steps']), item['step_num'], msg = 'steps number correct.')

                if len(item['more']) > 0:
                    for item2 in range(0, len(item['more'])):
                        for field4 in more_fields:
                            self.assertIn(field4, item['more'][item2], msg = 'more content had field \'%field4\'.')

                    for item3 in range(0, len(item['more'])-1):    
                        self.assertGreater(item['more'][item2]['id'], item['more'][item2+1]['id'], msg = 'more content ordered by id.')
                        self.assertGreater(item['more'][item2]['create_time'], item['more'][item2+1]['create_time'],
                                msg = 'more content ordered by create time.')
                        
                        self.assertFalse(item['more'][item2]['id']==item['id'], msg = 'more content \'id\' correct.')

                        more_url = item['more'][item2]['url']
                        more_response = requests.get(more_url)
                        self.assertEqual(more_response.status_code, 200, msg = 'more response status code equals to 200.')

                else:
                    pass

                dish_url = item['url']
                
                if len(dishes_response_content) > 0:
                    for i in range(0, len(dishes_response_content)-1):   
                        self.assertGreater(dishes_response_content[i].get('id'), dishes_response_content[i+1].get('id'),
                                msg = 'dishes response content ordered by id.')
                else:
                    print "dish response content is null."

                pre_create_time = None
                if not pre_create_time:
                    pre_create_time = item['create_time']
                else:
                    current_create_time = item['create_time']
                    self.assertGreater(current_create_time, pre_create_time, msg = 'response content ordered by create time.')
                    pre_create_time = current_create_time

                dish_fields = ['url', 'id', 'name', 'user', 'desc', 'cover', 'status', 'tag', 'tips', 'create_time', 'steps',
                        'step_num', 'more', 'card_url']
                dish_response = requests.get(dish_url)
                self.assertEqual(dish_response.status_code, 200, msg = 'dish response status code equals to 200.')
                try:
                    dish_response_content = json.loads(dish_response.content)
                    for field5 in dish_fields:
                        self.assertIn(field5, dish_response_content, msg = 'dish response content had field \'%s\'.' % field5)
                        for field6 in user_required_fields:
                            self.assertIn(field6, dish_response_content.get('user'), msg = 'dish user content had field \'%field6\'.')
                        for field7 in steps_fields:
                            self.assertIn(field7, dish_response_content.get('steps'), msg = 'dish steps content had field \'field7\'.')
                        self.assertEqual(len(dish_response_content.get('steps')), dish_response_content.get('step_num'),
                                msg ='dish step number correct.')

                        self.assertEqual(item[field5], dishes_response_content.get(field5), msg = 'dish content correct.')

                except exceptions.ValueError, e:
                    self.assertTrue(False, msg = 'dish response content is json.')
        
        except exceptions.ValueError,e:
            self.assertTrue(False, msg = 'dishes response content is json.')


    def test_dishes_pagination(self):
        pass









class Test_Add_Dishes(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_add_dish(self):
        pass

    def test_add_dish_without_authorization(self):
        pass

    def test_add_dish_without_some_fields(self):
        pass

    def test_add_dish_with_wrong_token(self):
        pass

    def test_add_dish_and_fetch_it_later(self):
        pass
