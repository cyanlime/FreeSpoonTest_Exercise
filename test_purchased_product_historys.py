import unittest
import requests
import json
import exceptions
import datetime

import urlparse
from urllib import urlencode

import utils

class Test_Purchased_Product_Historys_View(unittest.TestCase):
    def setUp(self):
        self.login_url = 'http://yijiayinong.com/api/business/login'
        self.bulks_url = 'http://yijiayinong.com/api/business/bulks/'
        self.purchased_product_historys_url = 'http://yijiayinong.com/api/business/purchasedproducthistorys/'
        self.mob = '18610178190'
        login_response = requests.post(self.login_url, data = {
            'mob': self.mob,
            'code': '123456'
        })
        login_response_content = json.loads(login_response.content)
        token = login_response_content.get('token')
        self.token = token
        

    def test_purchased_product_historys_view(self):
        headers = {
            'Authorization': 'JWT % s' % self.token
        }
        history_response = requests.get(self.purchased_product_historys_url, headers = headers)
        self.assertEqual(history_response.status_code, 400, msg = 'response status code equals to 400.')

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
                                    'create_time', 'details', 'participant_count', 'purchased_count', 'tag', 'tag_color',
                                    'participant_avatars', 'history']
                        details_fields = ['image', 'plain', 'seq', 'width', 'height']
                        history_fields = ['order_id', 'bulk_id', 'product_id', 'name', 'quantity', 'spec', 'create_time']
                
                        for i2 in range(0, len(bulk_response_content.get('products'))):
                            for field2 in products_fields:
                                if field2 not in products_fields:
                                    print bulk_response_content.get('products')[i2][id]
                                self.assertIn(field2, bulk_response_content.get('products')[i2], 
                                    msg = 'product %s had field \'%s\'.' % (bulk_response_content.get('products')[i2]['id'], field2))
                            self.assertLessEqual(len(bulk_response_content.get('products')[i2].get('participant_avatars')), 6,
                                    msg = 'participant avatars amount less than 6.')

                            for i3 in range(0, len(bulk_response_content.get('products')[i2].get('details'))):
                                for field3 in details_fields:
                                    self.assertIn(field3, bulk_response_content.get('products')[i2].get('details')[i3], 
                                            msg = 'detail had field \'%s\'.' % field3)
                                    self.assertEqual(bulk_response_content.get('products')[i2].get('details')[i3].get('seq'), i3+1, 
                                            msg = 'detail seq correct.')
                            product_url = bulk_response_content.get('products')[i2].get('url')
                            history_url = bulk_response_content.get('products')[i2].get('history')                


                            history_response = requests.get(history_url, headers = headers)
                            self.assertEqual(history_response.status_code, 200, msg = 'history response status code equals to 200.')
                            try:
                                history_response_content = json.loads(history_response.content)
                                for i4 in range(0, len(history_response_content)):
                                    for field4 in history_fields:
                                        self.assertIn(field4, history_response_content[i4], 
                                                msg = 'history response content had field \'%s\'.' % field4)
                                    
                                if (len(history_response_content) > 0):
                                    for i5 in range(0, len(history_response_content)-1):
                                        if history_response_content[i5].get('create_time') < history_response_content[i5+1].get('create_time'):
                                            print history_response_content[i5].get('create_time')
                                        self.assertGreaterEqual(history_response_content[i5].get('create_time'), 
                                                history_response_content[i5+1].get('create_time'), 
                                                msg = 'history response content ordered by create time. %s' 
                                                    % history_response_content[i5+1].get('create_time'))

                                else:
                                    print 'purchase create time: %s' % create_timehistory_response_content[i5].get('create_time')

                            except exceptions.ValueError, e:
                                self.assertTrue(False, msg = 'response content is json.')

                    except exceptions.ValueError, e:
                        self.assertTrue(False, msg = 'response content is json.')

        except exceptions.ValueError, e:
            self.assertTrue(False, msg = 'response content is json.')


    def test_purchased_product_historys_pagination(self):
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
                                    'create_time', 'details', 'participant_count', 'purchased_count', 'tag', 'tag_color',
                                    'participant_avatars', 'history']
                        details_fields = ['image', 'plain', 'seq', 'width', 'height']
                        history_fields = ['order_id', 'bulk_id', 'product_id', 'name', 'quantity', 'spec', 'create_time']
                
                        for i2 in range(0, len(bulk_response_content.get('products'))):
                            for field2 in products_fields:
                                if field2 not in products_fields:
                                    print bulk_response_content.get('products')[i2][id]
                                self.assertIn(field2, bulk_response_content.get('products')[i2], 
                                    msg = 'product %s had field \'%s\'.' % (bulk_response_content.get('products')[i2]['id'], field2))
                            self.assertLessEqual(len(bulk_response_content.get('products')[i2].get('participant_avatars')), 6,
                                    msg = 'participant avatars amount less than 6.')

                            for i3 in range(0, len(bulk_response_content.get('products')[i2].get('details'))):
                                for field3 in details_fields:
                                    self.assertIn(field3, bulk_response_content.get('products')[i2].get('details')[i3], 
                                            msg = 'detail had field \'%s\'.' % field3)
                                    self.assertEqual(bulk_response_content.get('products')[i2].get('details')[i3].get('seq'), i3+1, 
                                            msg = 'detail seq correct.')
                            product_url = bulk_response_content.get('products')[i2].get('url')
                            history_url = bulk_response_content.get('products')[i2].get('history')       
        
                            epoch = datetime.datetime(1970, 1, 1)
                            now = datetime.datetime.now()
                            time = utils.totalMicroseconds(now - epoch)
                            page_size = 5
                            history_pagination_url = utils.addQueryParams(history_url, {
                                'page_size': page_size,
                                'time': time
                            })
                            historys_page_response = requests.get(history_pagination_url)
                            self.assertEqual(historys_page_response.status_code, 200, 
                                    msg = 'historys_page_response status code equals to 200.')
                            try:
                                historys_page_response_content = json.loads(historys_page_response_content)
                                self.assertIsInstance(historys_page_response_content, list, 
                                    msg = 'history page response content is a list.')
                                self.assertEqual(len(historys_page_response_content), page_size, 
                                    msg = 'history page response content length no more than parameter %s.' % page_size)

                                pre_create_time = None
                                for item in range(0,len(historys_page_response_content)):
                                    if not pre_create_time:
                                        pre_create_time = historys_page_response_content[item].get('create_time')
                                    else:
                                        current_create_time = historys_page_response_content[item].get('create_time')
                                        self.assertGreaterEqual(pre_create_time, current_create_time, 
                                                msg = 'historys_page_response content ordered by create time.')
                                        pre_create_time = current_create_time
                                        self.assertLess(pre_create_time, time, msg = 'create time no more than parameter %s' % time)

                            except exceptions.ValueError, e:
                                self.assertTrue(False, msg = 'historys page response content is json.')
                    except exceptions.ValueError, e:
                                self.assertTrue(False, msg = 'historys page response content is json.')
        except exceptions.ValueError, e:
                                self.assertTrue(False, msg = 'historys page response content is json.')
