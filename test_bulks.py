import unittest
import requests
import json
import exceptions
import datetime

import urlparse
from urllib import urlencode

import utils

class Test_Bulks_View(unittest.TestCase):
    def setUp(self):
        self.login_url = 'http://yijiayinong.com/api/business/login'
        self.bulks_url = 'http://yijiayinong.com/api/business/bulks/'
        self.mob = '18610178190'
        login_response = requests.post(self.login_url, data = {
            'mob': self.mob,
            'code': '123456'
        })
        login_response_content = json.loads(login_response.content)
        token = login_response_content.get('token')
        self.token = token


    def test_fetch_bulks_with_authorization(self):
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
            reseller_fields = ['id', 'name', 'tail', 'create_time']
            status_code = [-1, 0]
            receive_mode = [1, 2, 3]

            for item in datacontent:
                for field in bulks_fields:
                    self.assertIn(field, item, msg = 'response content had field \'%s\'.' % field)

                for i in range(0, len(datacontent)):
                    for field2 in reseller_fields:
                        self.assertIn(field2, datacontent[i].get('reseller'), msg = 'reseller had field \'%s\'.' % field2)

                    self.assertGreater(datacontent[i].get('dead_time'), datacontent[i].get('create_time'), 
                            msg = 'dead time is greater than create time. % s' % datacontent[i].get('id'))
                    self.assertGreater(datacontent[i].get('arrived_time'), datacontent[i].get('creat_time'),
                            msg = 'arrived time is greater than create time.')
                    self.assertLessEqual(datacontent[i].get('dead_time'), datacontent[i].get('arrived_time'),
                            msg = 'dead time is less equal than arrived time. % s' % datacontent[i].get('id'))
                    
                    self.assertIn(datacontent[i].get('status'), status_code, msg = 'status code is correct.')
                    self.assertIn(datacontent[i].get('receive_mode'), receive_mode, 
                            msg = 'receive mode %s is correct.' % datacontent[i].get('id'))

                    itemcovers = datacontent[i].get('covers')
                    for i2 in range(0, len(itemcovers)):
                        covers_response = requests.get(itemcovers[i2], headers = headers)
                        self.assertEqual(covers_response.status_code, 200, msg = 'cover response content status code equals to 200.')                   
                

                if len(datacontent) > 0:
                    for i4 in range(0, len(datacontent)-1):
                        if datacontent[i4].get('dead_time') < datacontent[i4+1].get('dead_time'):
                            print i4
                        self.assertGreaterEqual(datacontent[i4].get('dead_time'), datacontent[i4+1].get('dead_time'), 
                                msg = 'bulks response order by deadtime.')
                        
                else:
                    print "datacontent length error"


                    bulk_url = datacontent[i].get('url')
                    bulk_response = requests.get(bulk_url, headers = headers)
                    self.assertEqual(bulk_response.status_code, 200, msg = 'bulk response content status code equals to 200.')
                    try:
                        bulk_response_content = json.loads(bulk_response.content)
                        bulk_fields = ['url', 'id', 'title', 'category', 'reseller', 'dispatchers', 'products', 'location',
                                'standard_time', 'dead_time', 'arrived_time', 'status', 'card_title', 'card_desc', 'card_url',
                                'create_time', 'participant_count', 'receive_mode']
                        dispatchers_fields = ['id', 'name', 'tail', 'address', 'create_time', 'opening_time', 'closing_time']
                        products_fields = ['url', 'id', 'title', 'desc', 'unit_price', 'market_price', 'spec', 'spec_desc', 
                                    'cover','create_time', 'details', 'participant_count', 'purchased_count', 'tag', 'tag_color',
                                    'participant_avatars', 'history']
                        details = ['image', 'plain', 'seq', 'width', 'height']
                        
                        
                        for field2 in bulk_fields:
                            self.assertIn(field2, bulk_response_content, msg = 'bulk response content had field \'% s\'.' % field2)

                            self.assertGreater(bulk_response_content.get('dead_time'), bulk_response_content.get('create_time'),
                                msg = 'dead time is greater than create time. %s' % bulk_response_content.get('id'))
                            self.assertGreater(bulk_response_content.get('arrived_time'), bulk_response_content.get('create_time'),
                                msg = 'arrived time is greater than create time. %s' % bulk_response_content.get('id'))
                        
                            self.assertIn(bulk_response_content.get('receive_mode'), receive_mode, msg = 'recieve mode correct.')

                        standard_time_value = bulk_response_content.get('standard_time')
                        dead_time_value = bulk_response_content.get('dead_time')
                        if (standard_time_value > dead_time_value):
                            self.assertEqual(bulk_response_content.get('status', -1), msg = 'reach deadline.')


                        for field3 in reseller_fields:
                            self.assertIn(field3, bulk_response_content.get('reseller'), 
                                    msg = 'bulk response content had field \'% s\'.' % field3)
                        for i3 in range(0, len(bulk_response_content.get('dispatchers'))):
                            for field4 in dispatchers_fields:
                                self.assertIn(field4, bulk_response_content.get('dispatchers')[i3],
                                        msg = 'bulk response content had field \'% s\'.' % field4)
                                
                                self.assertLessEqual(bulk_response_content.get('dispatchers')[i3].get('opening_time'), 
                                            bulk_response_content.get('dispatchers')[i3].get('closing_time'), 
                                        msg = 'opening time less equal than closing time.')
                                   
                    
                    except exceptions.ValueError, e:
                        self.assertTrue(False, msg = 'bulk response content is json.')   

        except exceptions.ValueError, e:
            self.assertTrue(False, msg = 'response content is json.')


    def test_fetch_bulks_without_authorization(self):
        response = requests.get(self.bulks_url)
        self.assertEqual(response.status_code, 200, msg = 'response status code equals to 200.')

    def test_bulks_pagination(self):
        epoch = datetime.datetime(1970, 1, 1)
        now = datetime.datetime.now()
        time = utils.totalMicroseconds(now - epoch)
        page_size = 5
        bulks_page_url = utils.addQueryParams(self.bulks_url, {
            'page_size': page_size,
            'time': time
        })

        bulks_page_response = requests.get(bulks_page_url)
        self.assertEqual(bulks_page_response.status_code, 200, 
                msg = 'bulks page response status code equals to 200.')
        try:
            bulks_page_response_content = json.loads(bulks_page_response.content)
            self.assertIsInstance(bulks_page_response_content, list, 
                    msg = 'bulks page response content is a list.')
            self.assertEqual(len(bulks_page_response_content), page_size, 
                    msg = 'bulks page response content length no more than page_size.')

            pre_dead_time = None            
            for item in range(0, len(bulks_page_response_content)):
                if not pre_dead_time:
                    pre_dead_time = bulks_page_response_content[item].get('dead_time')
                else:
                    current_dead_time = bulks_page_response_content[item].get('dead_time')
                    self.assertLessEqual(current_dead_time, pre_dead_time, 
                            msg = 'bulk page response content ordered by dead time.')
                    print current_dead_time
                    pre_dead_time = current_dead_time
                self.assertGreater(pre_dead_time, time, msg = 'bulks %s dead time less than parameter \'time\'.' % bulks_page_response_content[item].get('url'))


        except exceptions.ValueError, e:
            self.assertTrue(False, msg = 'bulks page response content is json.') 