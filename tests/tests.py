# -*- coding: utf-8 -*-
'''
Created on Jan 3, 2014

@author: joaograca
'''

import os
import unittest
import requests_mock

from unbabel.api import (UnbabelApi, LangPair, Tone, Topic,
                         Translation, Account, BadRequestException)


class TestUnbabelAPI(unittest.TestCase):
    user = None
    key = None

    @property
    def api(self):
        if not hasattr(self, '_api'):
            self._api = UnbabelApi(self.user, self.key)
        return self._api

    @requests_mock.Mocker()
    def test_api_get_language_pairs(self, m):
        m.get('/tapi/v2/language_pair/', json={"objects": [{
            "lang_pair": {
                "source_language": {
                    "name": "Portuguese",
                    "shortname": "pt"
                },
                "target_language": {
                    "name": "English",
                    "shortname": "en"
                }
            }
        }]})

        pairs = self.api.get_language_pairs()

        self.assertIsInstance(pairs, list, 'Got something that is not a list')
        self.assertGreater(len(pairs), 0, 'Got 0 pairs')
        self.assertTrue(
            reduce(lambda x, y: x and y,
                   [isinstance(p, LangPair) for p in pairs]),
            'The pairs are not all instance of LangPair')

    @requests_mock.Mocker()
    def test_api_get_available_tones(self, m):
        m.get('/tapi/v2/tone/', json={
            "objects": [
                {
                    "tone": {
                        "description": "Informal style",
                        "name": "Informal"
                    }
                },
                {
                    "tone": {
                        "description": "Formal style",
                        "name": "Formal"
                    }
                }
            ]
        })
        tones = self.api.get_tones()

        self.assertIsInstance(tones, list, 'Got something that is not a list')
        self.assertGreater(len(tones), 0, 'Got 0 tones')
        self.assertTrue(
            reduce(lambda x, y: x and y,
                   [isinstance(t, Tone) for t in tones]),
            'The tones are not all instance of Tone')

    @requests_mock.Mocker()
    def test_api_get_topics(self, m):
        m.get('/tapi/v2/topic/', json={
            "objects": [
                {
                    "topic": {
                        "name": "politics"
                    }
                }
            ]})
        topics = self.api.get_topics()

        self.assertIsInstance(topics, list, 'Got something that is not a list')
        self.assertGreater(len(topics), 0, 'Got 0 topics')
        self.assertTrue(
            reduce(lambda x, y: x and y,
                   [isinstance(t, Topic) for t in topics]),
            'The topics are not all instance of Topic')

    @requests_mock.Mocker()
    def test_api_post_translation(self, m):
        data = {
            'text': "This is a test translation",
            'source_language': 'en',
            'target_language': 'pt',
        }
        m.get('/tapi/v2/account/', json={
            "objects": [
                {
                    "account": {
                        "balance": 1234.0,
                        "email": "emailaddress@test.com",
                        "username": "username"
                    }
                }
            ]
        })
        account = self.api.get_account()
        m.post("/tapi/v2/translation/", json={
            "callback_url": "http://www.mocky.io/v2/5c4065190f00007b0ae7b42d",
            "order_number": 109,
            "price": 10,
            "source_language": "en",
            "status": "new",
            "target_language": "pt",
            "text": "Hello World",
            "text_format": "text",
            "uid": "5c4065190f00007b0ae7b42d-w",
            "brand": "brand-x"
        }, status_code=201)
        translation = self.api.post_translations(**data)
        self.assertIsInstance(translation, Translation,
                              'Should get a Translation instance')
        self.assertIsNotNone(translation.uid, 'Did not get a uid')
        self.assertGreater(translation.price, 0, 'Price is not greater than 0')
        self.assertEqual(translation.source_language, 'en',
                         'Source language is not en but %s'
                         % translation.source_language)
        self.assertEqual(translation.target_language, 'pt',
                         'Target language is not pt but %s'
                         % translation.target_language)
        self.assertEqual(translation.text, "Hello World")
        self.assertEqual(translation.status, 'new',
                         'Wrong status: [{}]'.format(translation.status))
        self.assertIsNone(translation.topics, 'Topics is not None')
        self.assertIsInstance(translation.translators, list,
                              'Translators is not a list')
        self.assertIsNone(translation.translation, 'Got a translation')
        self.assertEqual(translation.brand, 'brand-x')

        account2 = self.api.get_account()
        self.assertEqual(account.balance + translation.price,
                         account2.balance + translation.price,
                         "Balance inconsistency after post translation")
        m.get("/tapi/v2/translation/5c4065190f00007b0ae7b42d-w/", json={
            "order_number": 109,
            "price": 10,
            "source_language": "en",
            "status": "new",
            "target_language": "pt",
            "text": "Hello World",
            "text_format": "text",
            "uid": "5c4065190f00007b0ae7b42d-w"
        })
        trans = self.api.get_translation(translation.uid)
        self.assertEqual(translation.uid, trans.uid, 'uids not equal')
        self.assertEqual(translation.source_language, trans.source_language,
                         'source language not equal')
        self.assertEqual(translation.source_language, trans.source_language,
                         'target language not equal')
        self.assertEqual(translation.price, trans.price, 'price not equal')
        self.assertEqual(translation.text, trans.text, 'text not equal')

    @requests_mock.Mocker()
    def test_api_get_account(self, m):
        m.get('/tapi/v2/account/', json={
            "objects": [
                {
                    "account": {
                        "balance": 1234.0,
                        "email": "emailaddress@test.com",
                        "username": "username"
                    }
                }
            ]
        })
        account = self.api.get_account()
        self.assertIsInstance(account, Account,
                              'Should be an Account instance')
        self.assertIsInstance(account.username, unicode,
                              'Username is not unicode')
        self.assertEqual(account.username, "username", 'Wrong username')
        self.assertIsInstance(account.balance, float, 'Balance is not float')
        self.assertIsInstance(account.email, unicode, 'Email is not unicode')

    @requests_mock.Mocker()
    def test_api_get_translations(self, m):
        m.get("/tapi/v2/translation/", json={
            "meta": {
                "limit": 20,
                "next": "/tapi/v2/translation?limit=20&offset=20",
                "offset": 0,
                "previous": None,
                "total_count": 40
            },
            "objects": [
                {
                    "order_number": 4,
                    "price": 40,
                    "source_language": "en",
                    "status": "completed",
                    "target_language": "pt",
                    "text": "foo",
                    "text_format": "text",
                    "translatedText": "arb",
                    "uid": "f06209d35e"
                },
            ]
        })
        translations = self.api.get_translations()
        self.assertIsInstance(translations, list,
                              'Translations is not a list!')
        self.assertTrue(len(translations) > 0,
                        'Translations list is empty!')
        self.assertTrue(all(isinstance(t, Translation) for t in translations),
                        'Items are not all instance of Translation')

    @requests_mock.Mocker()
    def test_api_unauthorized_call(self, m):
        m.get("/tapi/v2/language_pair/", status_code=401, json={
            "code": "401",
            "error": "Unauthorized"
        })
        api = self.api
        self._api = UnbabelApi(username='fake_username',
                               api_key='fake_api_key')

        pairs = self.api.get_language_pairs()
        self.assertIsInstance(pairs, list, 'Got something that is not a list')

        self._api = api

    @requests_mock.Mocker()
    def test_job_no_balance(self, m):
        self.user = "user-1"
        self.key = "xxxx"
        if hasattr(self, '_api'): delattr(self, '_api')

        data = {
            'text': "This is a test translation",
            'source_language': 'en',
            'target_language': 'pt'
        }

        self.assertEqual(
            self.api.username,
            "user-1", "API Username not correct %s" % self.api.username)
        self.assertEqual(self.api.api_key, "xxxx",
                         "API key not correct %s" % self.api.api_key)

        m.post("/tapi/v2/translation/", json={
            "callback_url": "http://www.mocky.io/v2/5c4065190f00007b0ae7b42d",
            "order_number": 109,
            "price": 10,
            "source_language": "en",
            "status": "insufficient_balance",
            "target_language": "pt",
            "text": "Hello World",
            "text_format": "text",
            "uid": "5c4065190f00007b0ae7b42d-w"
        }, status_code=201)
        translation = self.api.post_translations(**data)
        self.assertEqual(
            translation.status, "insufficient_balance",
            'Job status not insufficient_balance but %s' % translation.status)

        self.UNBABEL_TEST_USERNAME = os.environ.get('UNBABEL_TEST_USERNAME')
        self.UNBABEL_TEST_API_KEY = os.environ.get('UNBABEL_TEST_API_KEY')
        if hasattr(self, '_api'): delattr(self, '_api')


if __name__ == "__main__":
    unittest.main()
