import unittest
import requests
import json
import exceptions

class Test_Product_View(unittest.TestCase):
    def setUp(self):
        self.login_url = 'http://yijiayinong.com/api/business/login'
        self.bulks_url = 'http://yijiayinong.com/api/business/bulks/'
        self.products_url = 'http://yijiayinong.com/api/business/products/'
        self.mob = '18610178190'
        login_response = requests.post(self.login_url, data = {
            'mob': self.mob,
            'code': '123456'
        })
        login_response_content = json.loads(login_response.content)
        token = login_response_content.get('token')
        self.token = token


    def test_fetch_product_with_authorization(self):
        headers = {
            'Authorization': 'JWT % s' % self.token
        }
        response = requests.get(self.bulks_url, headers = headers)
        self.assertEqual(response.status_code, 200, msg = 'response status code equals to 200.')
        try:
            datacontent = json.loads(response.content)
            self.assertLessEqual(len(datacontent), 10, msg = 'response content length no more than 10.')
            self.assertIsInstance(datacontent, list, msg = 'response content is a list.')

            bulks_fields = ['url', 'id', 'title', 'category', 'reseller', 'covers', 'dead_time', 'arrived_time', 'status', 
                    'receive_mode', 'create_time', 'location', 'participant_count']

            for item in datacontent:
                for field in bulks_fields:
                    self.assertIn(field, item, msg = 'response content had field \'%s\'.' % field)
                for i in range(0, len(datacontent)):    
                    bulk_url = datacontent[i].get('url')
                    bulk_response = requests.get(bulk_url, headers = headers)
                    self.assertEqual(bulk_response.status_code, 200, msg = 'bulk response content status code equals to 200.')
                    try:
                        bulk_response_content = json.loads(bulk_response.content)
                        products_fields = ['url', 'id', 'title', 'desc', 'unit_price', 'market_price', 'spec', 'spec_desc', 'cover',
                                    'create_time', 'details', 'participant_count', 'purchased_count', 'tag', 
                                    'participant_avatars', 'history']
                        details_fields = ['image', 'plain', 'seq', 'width', 'height']
                
                        for i2 in range(0, len(bulk_response_content.get('products'))):
                            for field2 in products_fields:
                                if field2 not in bulk_response_content.get('products')[i2]:
                                    print bulk_response_content.get('products')[i2]['id']
                                self.assertIn(field2, bulk_response_content.get('products')[i2], 
                                    msg = 'product %s had field \'%s\'.' % (bulk_response_content.get('products')[i2]['id'], field2))
                            self.assertLessEqual(len(bulk_response_content.get('products')[i2].get('participant_avatars')), 6,
                                    msg = 'participant avatars amount less than 6.')

                            for i3 in range(0, len(bulk_response_content.get('products')[i2].get('details'))):
                                for field3 in details_fields:
                                    self.assertIn(field3, bulk_response_content.get('products')[i2].get('details')[i3], 
                                            msg = 'detail had field \'%s\'.' % field3)
                                    self.assertEqual(bulk_response_content.get('products')[i2].get('details')[i3].get('seq'), i3+1, 
                                            msg = 'detail seq correct. %s' % bulk_response_content.get('products')[i2])
                            product_url = bulk_response_content.get('products')[i2].get('url')
                            history_url = bulk_response_content.get('products')[i2].get('history')

                            product_fields = ['url', 'id', 'title', 'desc', 'unit_price', 'market_price', 'spec', 'spec_desc', 'cover', 'create_time', 'details', 'bulk_url']
                            
                            product_response = requests.get(product_url, headers = headers)
                            self.assertEqual(product_response.status_code, 200, msg = 'response status code equals to 200.')
                            try:
                                product_response_content = json.loads(product_response.content)
                                
                                for field4 in product_fields:
                                    self.assertIn(field4, product_response_content, msg = 'product response content had field \'%s\'.' % field4)
                                #self.assertLessEqual(product_response_content.get('unit_price'), product_response_content.get('market_price'),
                                            #msg = 'unit price is less or equal than market price.')
                                
                                bulk_url = product_response_content.get('bulk_url')
                                bulk_url_response = requests.get(bulk_url, headers = headers)
                                self.assertEqual(bulk_url_response.status_code, 200, msg = 'bulk url response status code equals to 200.')
                                                           
                                for i5 in range(0, len(product_response_content.get('details'))):
                                    for field5 in details_fields:
                                        self.assertIn(field5, product_response_content.get('details')[i5], msg = 'detail had field \'%s\'.' % field5)
                                        self.assertEqual(product_response_content.get('details')[i5].get('seq'), i5+1, msg = 'detail seq correct.')            


                            except exceptions.ValueError, e:
                                self.assertTrue(False, msg = 'response content is json.')


                    except exceptions.ValueError,e:
                        self.assertTrue(False, msg = 'response content is json.')

        except exceptions.ValueError,e:
            self.assertTrue(False, msg = 'response content is json.')



    def fetch_product_without_authorization(self):
        pass

    def fetch_products_with_authorization(self):
        headers = {
            'Authorization': 'JWT %s' % self.token
        }
        products_response = requests.get(self.products_url, headers = headers)
        self.assertEqual(products_response.status_code, 400, msg = 'products response status code equals to 400.')

    def fetch_products_without_authorization(self):
        products_response = requests.get(self.products_url, headers = headers)
        self.assertEqual(products_response.status_code, 400, msg = 'products response status code equals to 400.')