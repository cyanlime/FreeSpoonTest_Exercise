import unittest
import requests
import json
import exceptions

class Test_Authorization(unittest.TestCase):

    def setUp(self):
        self.login_url = 'http://yijiayinong.com/api/business/login'
        self.mob = '18600113725'

    def test_login(self):
        r = requests.post(self.login_url, data = {
            'mob': self.mob, 
            'code': '123456'
        })
        self.assertEqual(r.status_code, 200, 
            msg = 'response status code equals to 200.')
        self.assertIsNotNone(r.content,
            msg = 'response content is not null.')
        try:
            result = json.loads(r.content)   #json str transfers to python obj
            self.assertIn('token', result,
                msg = 'The result has field \'token\'')
        except Exception, e:   
            self.assertNotIsInstance(e, exceptions.ValueError,
                msg = 'reponse content is json')
      
    def test_without_mob_with_code(self):
        r = requests.post(self.login_url, data = {
            'code': '123456'
        }) 
        self.assertEqual(r.status_code, 400,
            msg = 'response status code equals to 400')

    def test_with_mob_without_code(self):
        r = requests.post(self.login_url, data = {
            'mob': self.mob
        })
        self.assertEqual(r.status_code, 400,
            msg = 'response status code equals to 400')

    def test_without_mob_without_code(self):
        r = requests.post(self.login_url)
        self.assertEqual(r.status_code, 400,
            msg = 'response status code equals to 400')

    def test_wrong_code(self):
        r = requests.post(self.login_url, data = {
            'mob': self.mob,
            'code': '654321'
        })
        self.assertEqual(r.status_code, 400,
            msg = 'response status code equals to 400.')

    def test_wrong_media_type(self):
        data = {
            'mob': self.mob,
            'code': '123456'
        }
        dataStr = json.dumps(data)
        r = requests.post(self.login_url, data = dataStr)
        self.assertEqual(r.status_code, 415,
            msg = 'response status code equals to 415.')

    def test_wrong_http_method(self):
        methods = ['get', 'put', 'patch', 'delete']
        for method in methods:
            r = getattr(requests, method)(self.login_url)
            self.assertEqual(r.status_code, 405,
                msg = 'response status code equals to 405 use method %s' % method)

    def test_method_options(self):
        r = requests.options(self.login_url, data = {
            'mob': self.mob,
            'code': '123456'
        })
        self.assertEqual(r.status_code, 200,
            msg = 'response status code equals to 200 use method options.')

