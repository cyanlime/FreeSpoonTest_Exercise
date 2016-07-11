import unittest
import requests
import json
import exceptions
import hashlib

class Test_Images(unittest.TestCase):
    def setUp(self):
        self.login_url = 'http://yijiayinong.com/api/business/login'
        self.images_url = 'http://yijiayinong.com/api/business/images/'
        login_response = requests.post(self.login_url, data = {
            'mob': '18610178190',
            'code': '123456'
        })
        login_response_content = json.loads(login_response.content)
        token = login_response_content.get('token')
        self.token = token

    def test_upload_images(self):
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
                self.assertIn('md5', upload_image_response_content, msg = 'response content had field \'md5\'.')
                self.assertEqual(md5, upload_image_response_content.get('md5'), msg = 'md5 value are consistent.')
                image_url = upload_image_response_content.get('image')

                fetch_image_response = requests.get(image_url)
                self.assertEqual(fetch_image_response.status_code, 200, msg = 'response status code equals to 200.')
                
                m2 = hashlib.md5()
                m2.update(fetch_image_response.content)
                self.assertEqual(md5, m2.hexdigest(), msg = 'md5 value are consistent.')


            except exceptions.ValueError, e:
                self.assertTrue(False, msg = 'response content is json.')
