import json
import os
import copy
import logging

import requests

from unbabel.abc import *
from unbabel.exceptions import UnauthorizedException, BadRequestException
from unbabel.translations import Translation, MTTranslation

log = logging.getLogger()

UNBABEL_SANDBOX_API_URL = os.environ.get(
    'UNBABEL_SANDOX_API_URL', 'https://sandbox.unbabel.com/tapi/v2/')
UNBABEL_API_URL = os.environ.get(
    'UNBABEL_API_URL', 'https://unbabel.com/tapi/v2/')


class UnbabelApi(object):
    def __init__(self, username, api_key, sandbox=False):
        '''
        The Unbabel Client object.

        :param username: Customer's username.
        :type username: str
        :param api_key: Customer's API key.
        :type api_key: str
        :param sandbox: Whether to use the sandbox API.
        :type sandbox: bool
        '''
        api_url = UNBABEL_SANDBOX_API_URL if sandbox else UNBABEL_API_URL

        self.username = username
        self.api_key = api_key
        self.api_url = api_url
        self.is_bulk = False
        self.headers = {
            'Authorization': 'ApiKey {}:{}'.format(self.username, self.api_key),
            'content-type': 'application/json'}

    def api_call(self, uri, data=None, internal_api_call=False):
        '''
        Wrapper function to fire GET/POST requests.

        :param uri: The request endpoint.
        :type uri: str
        :param data: The payload.
        :param internal_api_call: Whether to re-route the endpoint to internal.
        :type internal_api_call: bool

        '''
        # Routes the URL appropriately.
        api_url = self.api_url
        if internal_api_call:
            api_url = api_url.replace('/tapi/v2/', '/api/v1/')
        url = "{}{}".format(api_url, uri)
        # Actual request firing.
        if data is None: # GET requests.
            return requests.get(url, headers=self.headers)
        # POST requests.
        return requests.post(url, headers=self.headers, data=json.dumps(data))

    def post_translations(self, text, target_language, source_language=None, type=None, tone=None, visibility=None,
                          public_url=None, callback_url=None, topics=None, instructions=None, uid=None,
                          text_format="text", target_text=None, origin=None, client_owner_email=None, context=None):
        data = {k: v for k, v in locals().items() if not v in (self, None)}

        if self.is_bulk:
            self.bulk_data.append(data)
            return

        return self._make_request(data)

    def post_mt_translations(self, text, target_language, source_language=None, tone=None, callback_url=None,
                             topics=None, instructions=None, uid=None, text_format="text", origin=None,
                             client_owner_email=None):
        data = {k: v for k, v in locals().iteritems() if not v in (self, None)}
        endpoint = "{}/mt_translation/".format(self.api_url)
        result = requests.post(endpoint, headers=self.headers, data=json.dumps(data))

        if result.status_code in (201, 202):
            json_object = json.loads(result.content)
            toret = self._build_mt_translation_object(json_object)
            return toret
        elif result.status_code == 401:
            raise UnauthorizedException(result.content)
        elif result.status_code == 400:
            raise BadRequestException(result.content)
        else:
            raise Exception("Unknown Error return status %d: %s",
                            result.status_code, result.content[0:100])

    def _build_translation_object(self, json_object):
        source_lang = json_object.get("source_language", None)
        translation = json_object.get("translation", None)
        status = json_object.get("status", None)

        translators = [Translator.from_json(t) for t in
                       json_object.get("translators", [])]

        translation = Translation(
            uid=json_object["uid"],
            text=json_object["text"],
            target_language=json_object.get('target_language', None),
            source_language=json_object.get('source_language', None),
            translatedText=json_object.get('translatedText', None),
            status=json_object.get('status', None),
            translators=translators,
            topics=json_object.get('topics', None),
            price=json_object.get('price', None),
            balance=json_object.get('balance', None),
            text_format=json_object.get('text_format', "text"),
            origin=json_object.get('origin', None),
            price_plan=json_object.get('price_plan', None),
            client=json_object.get('client', None),
        )
        return translation

    def _build_mt_translation_object(self, json_object):
        source_lang = json_object.get("source_language", None)
        translation = json_object.get("translation", None)
        status = json_object.get("status", None)

        translation = MTTranslation(
            uid=json_object["uid"],
            text=json_object["text"],
            target_language=json_object.get('target_language', None),
            source_language=json_object.get('source_language', None),
            translatedText=json_object.get('translatedText', None),
            status=json_object.get('status', None),
            topics=json_object.get('topics', None),
            text_format=json_object.get('text_format', "text"),
            origin=json_object.get('origin', None),
            client=json_object.get('client', None),
        )
        return translation

    def _make_request(self, data):

        # headers={'Authorization': 'ApiKey %s:%s'%(self.username,
        # self.api_key),'content-type': 'application/json'}
        if self.is_bulk:
            f = requests.patch
        else:
            f = requests.post
        print(self.headers)
        result = f("%stranslation/" % self.api_url, headers=self.headers,
                   data=json.dumps(data))
        if result.status_code in (201, 202):
            json_object = json.loads(result.content)
            toret = None
            if self.is_bulk:
                toret = []
                for obj in json_object['objects']:
                    toret.append(self._build_translation_object(obj))
            else:
                toret = self._build_translation_object(json_object)
            return toret
        elif result.status_code == 401:
            raise UnauthorizedException(result.content)
        elif result.status_code == 400:
            raise BadRequestException(result.content)
        else:
            raise Exception("Unknown Error return status %d: %s",
                            result.status_code, result.content[0:100])

    def start_bulk_transaction(self):
        self.bulk_data = []
        self.is_bulk = True

    def _post_bulk(self):
        data = {'objects': self.bulk_data}
        return self._make_request(data=data)

    def post_bulk_translations(self, translations):
        self.start_bulk_transaction()
        for obj in translations:
            obj = copy.deepcopy(obj)
            text, target_language = obj['text'], obj['target_language']
            del obj['text']
            del obj['target_language']
            self.post_translations(text, target_language, **obj)

        return self._post_bulk()

    def get_translations(self, status=None):
        '''
            Returns the translations requested by the user
        '''
        if status is not None:
            result = self.api_call('translation/?status=%s' % status)
        else:
            result = self.api_call('translation/')
        if result.status_code == 200:
            translations_json = json.loads(result.content)["objects"]
            translations = [Translation(**tj) for tj in translations_json]
        else:
            log.critical(
                'Error status when fetching translation from server: {'
                '}!'.format(
                    result.status_code))
            translations = []
        return translations

    def get_translation(self, uid):
        '''
            Returns a translation with the given id
        '''
        result = self.api_call('translation/{}/'.format(uid))
        if result.status_code == 200:
            translation = Translation(**json.loads(result.content))
        else:
            log.critical(
                'Error status when fetching translation from server: {'
                '}!'.format(
                    result.status_code))
            raise ValueError(result.content)
        return translation

    def upgrade_mt_translation(self, uid, properties=None):
        """
        :param uid:
        :param properties: This is suppose to be a dictionary with new
        properties values to be replaced on the upgraded job
        :return:
        """
        api_url = self.api_url
        uri = 'mt_translation/{}/'.format(uid)
        url = "{}{}".format(api_url, uri)
        data = {"status": "upgrade", "properties": properties}
        return requests.patch(url, headers=self.headers, data=json.dumps(data))

    def get_mt_translations(self, status=None):
        '''
            Returns the translations requested by the user
        '''
        if status is not None:
            result = self.api_call('mt_translation/?status=%s' % status)
        else:
            result = self.api_call('mt_translation/')
        if result.status_code == 200:
            translations_json = json.loads(result.content)["objects"]
            translations = [Translation(**tj) for tj in translations_json]
        else:
            log.critical(
                'Error status when fetching machine translation from server: '
                '{}!'.format(
                    result.status_code))
            translations = []
        return translations

    def get_mt_translation(self, uid):
        '''
            Returns a translation with the given id
        '''
        result = self.api_call('mt_translation/{}/'.format(uid))
        if result.status_code == 200:
            translation = Translation(**json.loads(result.content))
        else:
            log.critical(
                'Error status when fetching machine translation from server: '
                '{}!'.format(
                    result.status_code))
            raise ValueError(result.content)
        return translation

    def get_language_pairs(self, train_langs=None):
        '''
            Returns the language pairs available on unbabel
        '''
        if train_langs is None:
            result = self.api_call('language_pair/')
        else:
            result = self.api_call(
                'language_pair/?train_langs={}'.format(train_langs))
        try:
            langs_json = json.loads(result.content)
            if 'error' in langs_json:
                return []
            languages = [LangPair(Language(
                shortname=lang_json["lang_pair"]["source_language"][
                    "shortname"],
                name=lang_json["lang_pair"]["source_language"]["name"]),
                Language(shortname=lang_json["lang_pair"][
                    "target_language"]["shortname"],
                         name=lang_json["lang_pair"][
                             "target_language"]["name"])
            ) for lang_json in langs_json["objects"]]
        except Exception as e:
            log.exception("Error decoding get language pairs")
            raise e
        return languages

    def get_tones(self):
        '''
            Returns the tones available on unbabel
        '''
        result = self.api_call('tone/')
        tones_json = json.loads(result.content)
        tones = [Tone(name=tone_json["tone"]["name"],
                      description=tone_json["tone"]["description"])
                 for tone_json in tones_json["objects"]]
        return tones

    def get_topics(self):
        '''
            Returns the topics available on unbabel
        '''
        result = self.api_call('topic/')
        topics_json = json.loads(result.content)
        topics = [Topic(name=topic_json["topic"]["name"])
                  for topic_json in topics_json["objects"]]
        return topics

    def get_account(self):
        result = self.api_call('account/')
        account_json = json.loads(result.content)
        account_data = account_json['objects'][0]['account']
        account = Account(**account_data)
        return account

    def get_word_count(self, text):
        result = self.api_call('wordcount/', {"text": text})

        if result.status_code == 201:
            json_object = json.loads(result.content)
            return json_object["word_count"]
        else:
            log.debug('Got a HTTP Error [{}]'.format(result.status_code))
            raise Exception("Unknown Error")

    def get_user(self):
        result = self.api_call('app/user/', internal_api_call=True)

        if result.status_code == 200:
            return json.loads(result.content)
        else:
            log.debug('Got a HTTP Error [{}]'.format(result.status_code))
            raise Exception("Unknown Error: %s" % result.status_code)


__all__ = ['UnbabelApi']
