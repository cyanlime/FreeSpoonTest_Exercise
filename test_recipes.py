import unittest
import requests
import json
import exceptions
import datetime
import copy
import hashlib

import urlparse
from urllib import urlencode

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
        self.images_url = 'http://yijiayinong.com/api/business/images/'        
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

        with open('json/recipe.json', 'r') as recipe_file:
            recipe_data = json.load(recipe_file)
            headers = {
                'Authorization': 'JWT %s' % self.token
            }
            
            with open('images/image1.jpg', 'rb') as image_file:
                m = hashlib.md5()
                m.update(image_file.read())
                md5 = m.hexdigest()
                image_file.seek(0)
                files = {
                    'file': image_file
                }
                image_response = requests.post(self.images_url, headers = headers, files = files)
                self.assertEqual(image_response.status_code, 201, msg = 'response status code equals to 201.')
                
                try:
                    image_response_content = json.loads(image_response.content)
                    self.assertIn('image', image_response_content, msg = 'image response content had field \'image\'.')
                    self.assertIn('md5', image_response_content, msg = 'image response content had field \'md5\'.')
                    
                    image_url = image_response_content.get('image')
                    image_md5 = image_response_content.get('md5')
                    self.assertEqual(image_md5, md5, msg = 'image md5 value are consist.')
                    get_image_response = requests.get(image_url, headers = headers)
                    self.assertEqual(get_image_response.status_code, 200, msg = 'image status code equals to 200.')

                    m = hashlib.md5()
                    m.update(get_image_response.content)
                    get_image_md5 = m.hexdigest()

                    self.assertEqual(get_image_md5, md5, msg = 'image md5 value are consist.')

                    recipe_data['cover'] = image_md5

                except exceptions.ValueError, E:
                    self.assertTrue(False, msg = 'response content is json.')


                post_response = requests.post(self.recipes_url, headers = headers, data = recipe_data)
                self.assertEqual(post_response.status_code, 201, msg = 'response status code equals to 201.')
                get_response = requests.get(self.recipes_url, headers = headers, data = recipe_data)
                self.assertEqual(get_response.status_code, 200, msg = 'response status code equals to 200.')

            try:
                post_recipe_data_content = json.loads(post_response.content)
                recipe_url = post_recipe_data_content.get('url')
                get_recipe_data_content = json.loads(get_response.content)
                
                fields = ['url', 'id', 'name', 'user', 'desc', 'cover', 'status', 'tag', 'tips', 'steps', 'dish_num', 'ingredients', 'step_num', 'create_time', 'more']
                recipe_fields = ['url', 'id', 'name', 'desc', 'tips', 'steps', 'ingredients']
                sim_fields = ['name', 'desc', 'tips']
                mul_fields = ['steps', 'ingredients']

                pre_create_time = None

                for item in get_recipe_data_content:   
                    if not pre_create_time:
                        pre_create_time = item.get('create_time')
                    else:
                        current_create_time = item.get('create_time')
                        self.assertGreater(pre_create_time, current_create_time, msg = 'recipes ordered by create time.')
                        pre_create_time = current_create_time
                                
                for field in recipe_fields:
                    self.assertIn(field, post_recipe_data_content, msg = 'recipe content had field \'field\'.')

                for item in sim_fields:      
                    self.assertEqual(recipe_data[item], post_recipe_data_content[item], msg = 'field \'%s\' is consistent between object.' % item)
        
                for item in mul_fields:                    
                    #demo
                    post_recipe_data_content =  recipe_data
                    list1 = recipe_data.get(item) 
                    list2 = post_recipe_data_content.get(item)

                    self.assertEqual(len(list1), len(list2))

                    for i in range(0, len(list1)):
                        for (key, value) in list1[i].items():
                            self.assertEqual(value, list2[i].get(key), msg = 'field \'%s\' value are the same.' % key)
                
                self.recipes.append(recipe_url)
            except exceptions.ValueError, e:
                self.assertTrue(False, msg = 'response content is json.')
      

    def test_add_recipe_without_authorization(self):
        with open('json/recipe.json') as f:
            recipe_data = json.load(f)
            response = requests.post(self.recipes_url, data = recipe_data)
            self.assertEqual(response.status_code, 461, msg = 'response status code equals to 461.')

    def test_add_recipe_without_some_fields(self):
       
        required_fields = ['name', 'cover', 'desc']
        optional_fields = ['tips', 'tag', 'steps', 'ingredients']

        headers = {
            'Authorization': 'JWT %s' % self.token
        }

        with open('json/recipe.json', 'r') as recipe_file:                         
            recipe_data = json.load(recipe_file)

            with open('images/image1.jpg', 'rb') as image_file:
                m = hashlib.md5()
                m.update(image_file.read())
                md5 = m.hexdigest()
                image_file.seek(0)
                files = {
                    'file': image_file
                }
                upload_image_response = requests.post(self.images_url, headers = headers, files = files)
                self.assertEqual(upload_image_response.status_code, 201, msg = 'response status code equals to 201.')

                try:
                    upload_image_response_content = json.loads(upload_image_response.content)
                    self.assertIn('image', upload_image_response_content, msg = 'response content had field \'image\'.')
                    self.assertIn('md5', upload_image_response_content, msg = 'response content had field \'md5\'.')
                    image_url = upload_image_response_content.get('image')
                    image_md5 = upload_image_response_content.get('md5')
                    self.assertEqual(image_md5, md5, msg = 'image md5 value are consist.')
                    
                    get_image_response = requests.get(image_url, headers = headers)
                    self.assertEqual(get_image_response.status_code, 200, msg = 'response status code equals to 200.')
                    
                    m = hashlib.md5()
                    m.update(get_image_response.content)
                    get_image_md5 = m.hexdigest()

                    self.assertEqual(get_image_md5, md5, msg = 'image md5 are consist.')

                    recipe_data['cover'] = md5

                except exceptions.ValueError, e:
                    self.assertTrue(False, msg = 'response content is json.')    
            
                   
                for field in required_fields:
                    required_recipe_data_copy = copy.deepcopy(recipe_data)
                    required_recipe_data_copy.pop(field)
                    response = requests.post(self.recipes_url, headers = headers, data = required_recipe_data_copy)
                    self.assertEqual(response.status_code, 400, msg = 'response status code equals to 400.')

                for field in optional_fields:
                    optional_recipe_data_copy = copy.deepcopy(recipe_data)
                    optional_recipe_data_copy.pop(field)
                    response = requests.post(self.recipes_url, headers = headers, data = optional_recipe_data_copy)
                    self.assertEqual(response.status_code, 201, msg = 'response status code equals to 201.')
                    response_content = json.loads(response.content)

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

            with open('images/image1.jpg', 'rb') as image_file:
                m = hashlib.md5()
                m.update(image_file.read())
                md5 = m.hexdigest()
                image_file.seek(0)
                files = {
                    'file': image_file
                }
                upload_image_response = requests.post(self.images_url, headers = headers, files = files)
                self.assertEqual(upload_image_response.status_code, 201, msg = 'response status code equals to 201.')

                try:
                    upload_image_response_content = json.loads(upload_image_response.content)

                    self.assertIn('image', upload_image_response_content, msg = 'response content had field \'image\'.')
                    self.assertIn('md5', upload_image_response_content, msg = 'respopnse content had field \'md5\' ')
                    image_url = upload_image_response_content.get('image')
                    image_md5 = upload_image_response_content.get('md5')
                    self.assertEqual(image_md5, md5, msg = 'image md5 value are consist.')

                    get_image_response = requests.get(image_url, headers = headers)
                    self.assertEqual(get_image_response.status_code, 200, msg = 'response status code equals to 200.')
                    m = hashlib.md5()
                    m.update(get_image_response.content)
                    get_image_md5 = m.hexdigest()
                    self.assertEqual(get_image_md5, md5, msg = 'image md5 value are consist.')                

                    recipe_data['cover'] = md5

                except exceptions.ValueError, e:
                    self.assertTrue(False, msg = 'response is json.')

                add_response = requests.post(self.recipes_url, headers = headers, data = recipe_data)
                self.assertEqual(add_response.status_code, 201, msg = 'response content status code error.')
                fields = ['url', 'id', 'name', 'user', 'desc', 'cover', 'status', 'tag', 'tips', 'steps', 'dish_num', 'ingredients', 'step_num', 'create_time', 'more']

                try:
                    add_response_content = json.loads(add_response.content)
                    self.assertGreater(len(add_response_content), 0, msg = 'response content length less than 0.')
                    recipe_url = add_response_content.get('url')

                    fetch_response = requests.get(recipe_url)
                    self.assertEqual(fetch_response.status_code, 200, msg = 'response content status code error.')
                    fetch_response_content = json.loads(fetch_response.content)

                    pre_create_time = None
                    for item in fields:
                        if not pre_create_time:
                            pre_create_time = add_response_content.get('create_time')
                        else:
                            current_create_time = add_response_content.get('create_tiem')
                            self.assertGreater(pre_create_time, current_create_time)
                            pre_create_time = current_create_time


                    recipe_fields = ['name', 'desc', 'cover', 'tips', 'time', 'steps', 'ingredients']
                    for recipe_field in recipe_fields:
                        self.assertIn(recipe_field, add_response_content)
                        self.assertIn(recipe_field, fetch_response_content)
                    
                    recipe_fields1 = ['name', 'desc', 'tips', 'time']
                    for item in recipe_fields1:
                        self.assertEqual(add_response_content[item], recipe_data[item])
                        self.assertEqual(fetch_response_content[item], recipe_data[item])
                    
                    recipe_fields2 = ['steps', 'ingredients']
                    #step_fields = ['image', 'plain', 'seq']
                    #ingredient = ['name', 'seq', 'quantity']               

                    for item in recipe_fields2:

                        #demo
                        add_response_content = recipe_data
                        fetch_response_content = recipe_data

                        list1 = recipe_data.get(item)
                        list2 = add_response_content.get(item)
                        list3 = fetch_response_content.get(item)

                        self.assertEqual(len(list1), len(list2))
                        self.assertEqual(len(list1), len(list3))

                        for i in range(0, len(list1)):
                            obj1 = list1[i]
                            obj2 = list2[i]
                            obj3 = list3[i]

                            for (key, value) in obj1.items():
                                self.assertEqual(value, obj2.get(key))
                                self.assertEqual(value, obj3.get(key))

                except exceptions.ValueError, e:
                    self.assertTrue(false, msg = 'response content is json.')

                self.recipes.append(recipe_url)
        