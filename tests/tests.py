# -*- coding: utf-8 -*-
'''
Created on Jan 3, 2014

@author: joaograca
'''
import os
import unittest
import uuid

from unbabel.api import (UnbabelApi, Order, LangPair, Tone, Topic,
                         Translation, Account, Job, BadRequestException)


UNBABEL_TEST_USERNAME = os.environ.get('UNBABEL_TEST_USERNAME')
UNBABEL_TEST_API_KEY = os.environ.get('UNBABEL_TEST_API_KEY')
UNBABEL_TEST_API_URL = os.environ.get('UNBABEL_TEST_API_URL')


class TestUnbabelAPI(unittest.TestCase):
    @property
    def api(self):
        if not hasattr(self, '_api'):
            self._api = UnbabelApi(username = UNBABEL_TEST_USERNAME,
                                   api_key = UNBABEL_TEST_API_KEY,
                                   sandbox = True)
            self._api.api_url = UNBABEL_TEST_API_URL
        return self._api

    def xtest_api_get_language_pairs(self):
        pairs = self.api.get_language_pairs()

        self.assertIsInstance(pairs, list, 'Got something that is not a list')
        self.assertGreater(len(pairs), 0, 'Got 0 pairs')
        self.assertTrue(
            reduce(lambda x, y: x and y,
                   [isinstance(p, LangPair) for p in pairs]),
            'The pairs are not all instance of LangPair')

    def xtest_api_get_available_tones(self):
        tones = self.api.get_tones()

        self.assertIsInstance(tones, list, 'Got something that is not a list')
        self.assertGreater(len(tones), 0, 'Got 0 tones')
        self.assertTrue(
            reduce(lambda x, y: x and y,
                   [isinstance(t, Tone) for t in tones]),
            'The tones are not all instance of Tone')

    def xtest_api_get_topics(self):
        topics = self.api.get_topics()

        self.assertIsInstance(topics, list, 'Got something that is not a list')
        self.assertGreater(len(topics), 0, 'Got 0 topics')
        self.assertTrue(
            reduce(lambda x, y: x and y,
                   [isinstance(t, Topic) for t in topics]),
            'The topics are not all instance of Topic')

    def xtest_api_post_translation(self):
        data = {
            'text': "This is a test translation",
            'source_language': 'en',
            'target_language': 'pt',
        }
        account = self.api.get_account()
        translation = self.api.post_translations(**data)
        self.assertIsInstance(translation, Translation,
                         'Should get a Translation instance')
        self.assertIsNotNone(translation.uid, 'Did not get a uid')
        self.assertGreater(translation.price, 0, 'Price is not greater than 0')
        self.assertEqual(translation.source_language, 'en',
                         'Source language is not en')
        self.assertEqual(translation.target_language, 'pt',
                         'Target language is not pt')
        self.assertEqual(translation.text, data['text'])
        self.assertEqual(translation.status, 'new', 'status is not new')
        self.assertIsNone(translation.topics, 'Topics is not None')
        self.assertIsInstance(translation.translators, list,
                              'Translators is not a list')
        self.assertIsNone(translation.translation, 'Got a translation')

        account2 = self.api.get_account()
        self.assertEqual(account.balance, account2.balance + translation.price,
                         "Balance inconsistency after post translation")

        trans = self.api.get_translation(translation.uid)
        self.assertEqual(translation.uid, trans.uid, 'uids not equal')
        self.assertEqual(translation.source_language, trans.source_language,
                         'source language not equal')
        self.assertEqual(translation.source_language, trans.source_language,
                         'target language not equal')
        self.assertEqual(translation.price, trans.price, 'price not equal')
        self.assertEqual(translation.text, trans.text, 'text not equal')
        self.assertEqual(translation.status, trans.status, 'status not equal')

    def xtest_api_get_account(self):
        account = self.api.get_account()
        self.assertIsInstance(account, Account,
                              'Should be an Account instance')
        self.assertIsInstance(account.username, unicode,
                              'Username is not unicode')
        self.assertEqual(account.username, UNBABEL_TEST_USERNAME,
                         'Wrong username')
        self.assertIsInstance(account.balance, float, 'Balance is not float')
        self.assertIsInstance(account.email, unicode, 'Email is not unicode')

    def test_api_get_translations(self):
        data = {
            'text': "This is a test translation",
            'source_language': 'en',
            'target_language': 'pt',
        }
        self.api.post_translations(**data)
        translations = self.api.get_translations()
        self.assertIsInstance(translations, list,
            'Translations is not a list!')
        self.assertTrue(len(translations) > 0,
            'Translations list is empty!')
        self.assertTrue(all(isinstance(t, Translation) for t in translations),
            'Items are not all instance of Translation')

    def xtest_order_post(self):
        order = self.api.post_order()
        self.assertIsInstance(order, Order, 'Result is not an Order')
        self.assertIsNotNone(order.id, 'ID is None')
        self.assertEqual(order.status, 'new', 'Order status is not new')
        self.assertEqual(order.price, 0, 'Price is not 0')

    def xtest_job_add_job_to_order(self):
        order = self.api.post_order()

        data = {
            'order_id': order.id,
            'text': "This is a test translation",
            'source_language': 'en',
            'target_language': 'pt',
        }

        job = self.api.post_job(**data)
        self.assertIsInstance(job, Job)
        self.assertEqual(job.order_id, order.id, 'Order ID is not equal')
        self.assertEqual(job.status, 'built', 'Job status is not built')
        self.assertEqual(job.text, data['text'], 'Job text is not correct')
        self.assertEqual(job.source_language, data['source_language'],
                         'Job source_language is not correct')
        self.assertEqual(job.target_language, data['target_language'],
                         'Job target_language is not correct')

    def xtest_job_fail_mandatory_fields(self):
        self.assertRaises(BadRequestException, self.api.post_job, 0, '', '', '')

    def xtest_api_unauthorized_call(self):
        api = self.api
        self._api = UnbabelApi(username='fake_username',
                               api_key='fake_api_key')

        pairs = self.api.get_language_pairs()
        self.assertIsInstance(pairs, list, 'Got something that is not a list')

        self._api = api

    def xtest_job_add_job_to_order_all_params(self):
        order = self.api.post_order()

        data = {
            'order_id': order.id,
            'uid': uuid.uuid4().hex,
            'text': "This is a test translation",
            'source_language': 'en',
            'target_language': 'pt',
            'target_text': u"Isto é uma tradução de teste",
            'text_format': 'text',
            'tone': 'Informal',
            'topic': ['startups', 'tech'],
            'visibility': 'private',
            'instructions': "Ok people, there's nothing to see here. go home!",
            'public_url': 'http://google.com',
            'callback_url': 'http://dev.unbabel.com/',
            'job_type': 'paid',
        }

        job = self.api.post_job(**data)
        self.assertIsInstance(job, Job)
        self.assertEqual(job.order_id, order.id, 'Order ID is not equal')
        self.assertEqual(job.status, 'built', 'Job status is not built')
        self.assertEqual(job.text, data['text'], 'Job text is not correct')
        self.assertEqual(job.source_language, data['source_language'],
                         'Job source_language is not correct')
        self.assertEqual(job.target_language, data['target_language'],
                         'Job target_language is not correct')


if __name__ == "__main__":
     unittest.main()