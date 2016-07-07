import unittest
import requests
import json
import exceptions
import datetime

import utils


class Test_Recipes_View(unittest.TestCase):
    
    def setUp(self):
        self.recipes_url = 'http://yijiayinong.com/api/business/recipes/'

    def test_fetch_recipes(self):
        response = requests.get(self.recipes_url)
        self.assertEqual(response.status_code, 200, msg = 'response content status code equals to 200.')
        try:
            datacontent = json.loads(response.content)
            self.assertLessEqual(len(datacontent), 10, msg = 'response content length not more than 10.')
            self.assertIsInstance(datacontent, list, msg = 'response content is a list.')

            pre_create_time = None

            fields = ['url', 'id', 'name','user', 'desc', 'cover', 'status', 'tips', 'steps', 'dish_num', 'ingredients', 'step_num', 'create_time', 'more']
            for item in datacontent:
                for field in fields:
                    self.assertIn(field, item, msg = 'response content had no field \'%s\'.' % field)
                    
                if not pre_create_time:
                    pre_create_time = item['create_time']
                       
                else:
                    current_create_time = item['create_time']
                    self.assertGreater(pre_create_time, current_create_time, msg = 'response content is ordered by create time.')
                    pre_create_time = current_create_time

                response2 = requests.get(item['url'])
                self.assertEqual(response2.status_code, 200, msg = 'response content status code equals to 200.')              
                datacontent2 = json.loads(response2.content)
                self.assertTrue(len(datacontent2) > 0, msg = 'response content length not less than 1.')
                fields2 = ['url', 'id', 'name', 'user', 'desc', 'cover', 'status', 'tips', 'steps', 'dish_num', 'ingredients', 'step_num', 'create_time', 'more']
                
                for field2 in fields2:
                    self.assertIn(field2, datacontent2, msg = 'response content had no field %s' % field2)
                    
        except exceptions.ValueError, e:
            self.assertTrue(false, msg = 'response content is json.')


        
    def test_pagination(self):
        epoch = datetime.datetime(1970, 1, 1)
        now = datetime.datetime.now()
        time = utils.totalMicroseconds(now - epoch)
        page_size = 5
        recipes_page_url = utils.addQueryParams(self.recipes_url, {
                'page_size': page_size,
                'time': time
        })

        response = requests.get(recipes_page_url)
        self.assertEqual(response.status_code, 200, msg = 'response content status code equals to 200.')
        try:
            datacontent = json.loads(response.content)
            self.assertIsInstance(datacontent, list, msg = 'response content is a list.')
            self.assertLessEqual(len(datacontent), page_size, msg = 'response content length no more than \'page_size\'')
            
            pre_create_time = None
            for item in datacontent:
                if not pre_create_time:
                    pre_create_time = item['create_time']
                else:
                    current_create_time = item['create_time']
                    self.assertGreater(pre_create_time, current_create_time, msg = 'response content is ordered by create time.')
                    pre_create_time = current_create_time
                self.assertLess(pre_create_time, time, msg = 'recipe create time less than parameter \'time\'.')

        except exceptions.ValueError, e:
            self.assertTrue(False, msg = 'response content is json.')


class Test_Add_Recipes(unittest.TestCase):
    
    def setUp(self):
        self.login_url = 'http://yijiayinong.com/api/business/login'
        self.recipes_url = 'http://yijiayinong.com/api/business/recipes/'        
        self.mob = '18610178190'
        login_response = requests.post(self.login_url, data = {
            'mob': self.mob,
            'code': '123456'
        })
        login_response_content = json.loads(login_response.content)
        self.token = login_response_content.get('token')
        self.recipes = []

    def tearDown(self):
        for recipe in self.recipes:
            headers = {
                'Authorization': 'JWT %s' % self.token
            }
            response = requests.delete(recipe, headers = headers)
      

    def test_add_recipe(self):
        with open('json/recipe.json', 'r') as f:
            recipe_data = json.load(f)
            headers = {
                'Authorization': 'JWT %s' % self.token
            }
            response = requests.post(self.recipes_url, headers = headers, data = recipe_data)
            self.assertEqual(response.status_code, 201, msg = 'response status code equals to 201.')

            try:
                recipe_data_content = json.loads(response.content)

                fields = ['url', 'id', 'name', 'desc', 'tips', 'steps', 'ingredients']

                pre_create_time = None

                for field in fields:
                    self.assertIn(field, recipe_data_content, msg = 'recipe content had field \'field\'.')
                self.assertEqual(recipe_data['name'], recipe_data_content['name'], msg = 'name is consistent between object.')
                self.assertEqual(recipe_data['desc'], recipe_data_content['desc'], msg = 'desc is consistent between object.')
                self.assertEqual(recipe_data['tips'], recipe_data_content['tips'], msg = 'tips is consistent between object.')
                
                if not pre_create_time:
                    pre_create_time = recipe_data_content.get('create_time')
                else:
                    current_create_time = recipe_data_content.get('create_time')
                    self.assertGreater(pre_create_time, current_create_time, msg = 'recipes ordered by create time.')
                    pre_create_time = current_create_time
                    
                self.recipes.append(recipe_data_content['url'])
                         
            except exceptions.ValueError, e:
                self.assertTrue(false, msg = 'recipe content is json.')
      
    def test_add_recipe_without_authorization(self):
        with open('json/recipe.json') as f:
            recipe_data = json.load(f)
            response = requests.post(self.recipes_url, data = recipe_data)
            self.assertEqual(response.status_code, 461, msg = 'response status code equals to 461.')

    def test_add_recipe_without_some_fields(self):
       
        required_fields = ['name', 'cover', 'desc']
        optional_fields = ['tips', 'tag', 'steps', 'ingredients']
        
        for field in required_fields:
            with open('json/recipe_miss_field_%s.json' % field, 'r') as recipe_file_miss_required_field:
                recipe_data_miss_required_field = json.load(recipe_file_miss_required_field)
                headers = {
                    'Authorization': 'JWT %s' % self.token
                }
                response = requests.post(self.recipes_url, headers = headers, data = recipe_data_miss_required_field)
                self.assertEqual(response.status_code, 400, msg = 'response content status code equals to 400.')

        for field in optional_fields:
            with open('json/recipe_miss_field_%s.json' % field, 'r') as recipe_file_miss_optional_field:
                recipe_data_miss_optional_field = json.load(recipe_file_miss_optional_field)
                headers = {
                    'Authorization': 'JWT %s' % self.token
                }
                response = requests.post(self.recipes_url, headers = headers, data = recipe_data_miss_optional_field)
                response_content = json.loads(response.content)
                self.assertEqual(response.status_code, 201, msg = 'response content status code equals to 201.')                
                self.recipes.append(response_content['url'])

    def test_add_recipe_with_wrong_token(self):
        with open('json/recipe.json') as recipe_file:
            recipe_data = json.load(recipe_file)
            headers = {
                'Authorization': 'JWT %s' % 123456
            }
            response = requests.post(self.recipes_url, headers = headers, data = recipe_data)
            self.assertEqual(response.status_code, 401, msg = 'response content status code equals to 401.')

    def test_add_recipe_and_fetch_it_later(self):
        with open('json/recipe.json') as recipe_file:
            recipe_data = json.load(recipe_file)
            headers = {
                'Authorization': 'JWT %s' % self.token
            }
            add_response = requests.post(self.recipes_url, headers = headers, data = recipe_data)
            self.assertEqual(add_response.status_code, 201, msg = 'response content status code error.')
            
            try:
                add_response_content = json.loads(add_response.content)
                self.assertGreater(len(add_response_content), 0, msg = 'response content length less than 0.')
                recipe_url = add_response_content.get('url')

                fetch_response = requests.get(recipe_url)
                self.assertEqual(fetch_response.status_code, 200, msg = 'response content status code error.')
                fetch_response_content = json.loads(fetch_response.content)
               
                recipe_fields = ['name', 'desc', 'cover', 'tips', 'time', 'steps', 'ingredients']
                for recipe_field in recipe_fields:
                    self.assertIn(recipe_field, add_response_content)
                    self.assertIn(recipe_field, fetch_response_content)
                
                recipe_fields1 = ['name', 'desc', 'tips', 'time']
                for item in recipe_fields1:
                    self.assertEqual(add_response_content[item], recipe_data[item])
                    self.assertEqual(fetch_response_content[item], recipe_data[item])
                
                recipe_fields2 = ['steps', 'ingredients']
                step_fields = ['image', 'plain', 'seq']
                ingredient = ['name', 'seq', 'quantity']               


                pre_create_time = None
                if not pre_create_time:
                    pre_create_time = add_response_content.get('create_time')
                else:
                    current_create_time = add_response_content.get('create_tiem')
                    self.assertGreater(pre_create_time, current_create_time)
                    pre_create_time = current_create_time


            except exceptions.ValueError, e:
                self.assertTrue(false, msg = 'response content is json.')

            self.recipes.append(recipe_url)
    