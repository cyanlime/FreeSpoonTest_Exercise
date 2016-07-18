# -*- coding: utf-8 -*-
import unittest
import requests
import json
import exceptions

import utils

class Test_Search(unittest.TestCase):
    def setUp(self):
        self.bulks_url = 'http://yijiayinong.com/api/business/bulks/'
        search_data = '鱼'

    def test_search(self):
        search_url = utils.addQueryParams(self.bulks_url, {
            'search': search_data
        })
        search_response = requests.get(search_url)
        self.assertEqual(search_response.status_code, 200, msg = 'search response status code equals to 200.')