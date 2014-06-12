'''
Created on Dec 13, 2013

@author: joaograca
'''
import json
import logging
import os
import requests


log = logging.getLogger()


UNBABEL_SANDBOX_API_URL = os.environ.get('UNBABEL_SANDOX_API_URL',
                                         "http://sandbox.unbabel.com/tapi/v2/")
UNBABEL_API_URL = os.environ.get('UNBABEL_API_URL',
                                 "https://www.unbabel.co/tapi/v2/")


class UnauthorizedException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BadRequestException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Language(object):
    def __init__(self, shortname, name):
        self.shortname = shortname
        self.name = name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Tone(object):
    def __init__(self, description, name):
        self.description = description
        self.name = name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Topic(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class LangPair(object):
    def __init__(self, source_language, target_language):
        self.source_language = source_language
        self.target_language = target_language

    def __repr__(self):
        return "%s_%s" % (
            self.source_language.shortname, self.target_language.shortname)

    def __str__(self):
        return "%s_%s" % (
            self.source_language.shortname, self.target_language.shortname)


class Translator(object):
    def __init__(self, first_name="", last_name="", picture_url="",
                 profile_url=""):
        self.first_name = first_name
        self.last_name = last_name
        self.picture_url = picture_url
        self.profile_url = profile_url

    @classmethod
    def from_json(cls, json):
        t = Translator(json["first_name"], json["last_name"],
                       json["picture_url"], json["profile_url"])
        return t


class Translation(object):
    def __init__(self,
                 uid=-1,
                 text="",
                 translatedText=None,
                 target_language="",
                 source_language=None,
                 status=None,
                 translators=[],
                 topics=None,
                 price=None,
                 **kwargs):
        self.uid = uid
        self.text = text
        self.translation = translatedText
        self.source_language = source_language
        self.target_language = target_language
        self.status = status
        self.translators = translators
        self.topics = topics
        self.price = price

    def __repr__(self):
        return "%s %s %s_%s" % (
            self.uid, self.status, self.source_language, self.target_language)

    def __str__(self):
        return "%s %s %s_%s" % (
            self.uid, self.status, self.source_language, self.target_language)


class Account(object):
    def __init__(self, username, email, balance):
        self.username = username
        self.email = email
        self.balance = balance

    def __unicode__(self):
        return u'email: {email}, balance: {balance}'.format(
            email=self.email, balance=self.balance,
        )


class Job(object):
    def __init__(self, uid, order_id, status, source_language, target_language,
                 text, price, priority, creation_date):
        self.uid = uid
        self.order_id = order_id
        self.status = status
        self.text = text
        self.price = price
        self.source_language = source_language
        self.target_language = target_language
        self.creation_date = creation_date
        self.priority = priority

    def __unicode__(self):
        return u'order_id: {}, uid: {}, status: {}'.format(
            self.order_id, self.uid, self.status)


class Order(object):
    def __init__(self, id, status, price):
        self.id = id
        self.status = status
        self.price = price

    def __unicode__(self):
        return u'{id} - {status} - {price}'.format(
            id=self.id,
            status=self.status,
            price=self.price,
        )


class UnbabelApi(object):
    def __init__(self, username, api_key, sandbox=False):
        if sandbox:
            api_url = UNBABEL_SANDBOX_API_URL
        else:
            api_url = UNBABEL_API_URL
        self.username = username
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            'Authorization': 'ApiKey {}:{}'.format(self.username,
                                                   self.api_key),
            'content-type': 'application/json'}

    def api_call(self, uri, data=None):
        url = "{}{}".format(self.api_url, uri)
        if data is None:
            return requests.get(url, headers=self.headers)
        return requests.post(url, headers=self.headers, data=json.dumps(data))

    def post_translations(self, text, target_language, source_language=None,
                          ttype=None, tone=None, visibility=None,
                          public_url=None, callback_url=None, topics=None,
                          instructions=None, uid=None):
        data = {
            "text": text,
            "target_language": target_language
        }
        if source_language:
            data["source_language"] = source_language
        if ttype:
            data["type"] = ttype
        if tone:
            data["tone"] = tone
        if visibility:
            data["visibility"] = visibility
        if public_url:
            data["public_url"] = public_url
        if callback_url:
            data["callback_url"] = callback_url
        if topics:
            data["topics"] = topics
        if instructions:
            data["instructions"] = instructions
        if uid:
            data["uid"] = uid
        result = self.api_call('translation/', data)
        if result.status_code == 201:
            log.debug(result.content)
            json_object = json.loads(result.content)
            source_lang = json_object.get("source_language", None)
            translation = json_object.get("translation", None)
            status = json_object.get("status", None)
            topics = json_object.get('topics', None)

            translators = [Translator.from_json(t) for t in
                           json_object.get("translators", [])]

            translation = Translation(uid=json_object["uid"],
                                      text=json_object["text"],
                                      target_language=target_language,
                                      source_language=source_lang,
                                      translation=translation,
                                      status=status,
                                      translators=translators,
                                      topics=topics,
                                      price=json_object['price'],
            )
            return translation
        elif result.status_code == 401:
            raise UnauthorizedException(result.content)
        elif result.status_code == 400:
            raise BadRequestException(result.content)
        else:
            raise Exception("Unknown Error")

    def get_translations(self):
        '''
            Returns the translations requested by the user
        '''
        result = self.api_call('translation/')
        translations_json = json.loads(result.content)["objects"]
        translations = [Translation(**tj) for tj in translations_json]
        return translations


    def get_translation(self, uid):
        '''
            Returns a translation with the given id
        '''
        result = self.api_call('translation/{}/'.format(uid))
        translation = Translation(**json.loads(result.content))
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
        except:
            log.exception("Error decoding get language pairs")
            languages = []
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

    def post_order(self):
        data = {} # no input data, it's just a clean post
        result = self.api_call('order/', data)
        if result.status_code == 201:
            json_object = json.loads(result.content)
            id = json_object.get('id')
            status = json_object.get('status')
            price = json_object.get('price')
            order = Order(id, status, price)
            return order
        elif result.status_code == 401:
            raise UnauthorizedException(result.content)
        elif result.status_code == 400:
            raise BadRequestException(result.content)
        else:
            raise Exception("Unknown Error")

    def post_job(self, order_id, text, source_language, target_language,
                 target_text='', text_format="text", uid=None, tone=None,
                 topic=[], visibility=None, instructions='', public_url=None,
                 callback_url=None, job_type='paid'):

        data = {
            'order': order_id,
            'text': text,
            'target_text': target_text,
            'text_format': text_format,
            'source_language': source_language,
            'target_language': target_language,
            'uid': uid,
            'tone': tone,
            'topic': topic,
            'visibility': visibility,
            'instructions': instructions,
            'public_url': public_url,
            'callback_url': callback_url,
            'type': job_type,
        }

        result = self.api_call('job/', data)

        if result.status_code == 201:
            json_object = json.loads(result.content)
            #log.debug(json_object)
            job = Job(
                uid=json_object['uid'],
                order_id=json_object['order'],
                status=json_object['status'],
                text=json_object['text'],
                price=json_object['price'],
                source_language=json_object['source_language'],
                target_language=json_object['target_language'],
                creation_date=json_object['creation_date'],
                priority=json_object['priority']
            )
            return job
        elif result.status_code == 401:
            raise UnauthorizedException(result.content)
        elif result.status_code == 400:
            raise BadRequestException(result.content)
        else:
            log.debug('Got a HTTP Error [{}]'.format(result.status_code))
            #log.debug(result.content)
            raise Exception("Unknown Error")

    def get_word_count(self, text):
        result = self.api_call('wordcount/', {"text": text})
        print result
        log.debug(result)

        # if(result["error"]):
        #     log.debug(result.error)
        #     raise Exception("Unknown Error")
        # else:
        #     return result.word_count
        pass


__all__ = ['UnbabelApi']
