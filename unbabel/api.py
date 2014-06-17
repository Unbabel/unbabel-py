'''
Created on Dec 13, 2013

@author: joaograca
'''



import requests
import json

import logging
logger = logging.getLogger()

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
    
    def __init__(self,shortname,name):
        self.shortname = shortname
        self.name = name
        
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name



class Tone(object):
    
    def __init__(self,description,name):
        self.description = description
        self.name = name
        
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name


class Topic(object):
    
    def __init__(self,name):
        self.name = name
        
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name


class LangPair(object):
    
    def __init__(self,source_language,target_language):
        self.source_language = source_language
        self.target_language = target_language
        
    def __repr__(self):
        return "%s_%s"%(self.source_language.shortname, self.target_language.shortname)
    
    def __str__(self):
        return "%s_%s"%(self.source_language.shortname, self.target_language.shortname)

class Translator(object):
    
    def __init__(self,first_name="",last_name="",picture_url="",profile_url=""):
        self.first_name = first_name
        self.last_name = last_name
        self.picture_url = picture_url
        self.profile_url = profile_url
    
    @classmethod
    def from_json(cls,json):
        t = Translator(json["first_name"],json["last_name"],json["picture_url"],json["profile_url"])
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
        return "%s %s %s_%s"%(self.uid,self.status,self.source_language, self.target_language)
    
    def __str__(self):
        return "%s %s %s_%s"%(self.uid,self.status,self.source_language, self.target_language)


class UnbabelApi(object):
    
    def __init__(self, username,api_key,sandbox=False):
        if sandbox:
            api_url= "http://sandbox.unbabel.com/tapi/v2/"
        else:
            api_url = "https://www.unbabel.co/tapi/v2/" 
        self.username = username
        self.api_key = api_key
        self.api_url = api_url
        self.is_bulk = False
    

    def post_translations(self,
                          text,
                          target_language,
                          source_language=None,
                          ttype=None,
                          tone=None,
                          visibility=None,
                          public_url=None,
                          callback_url = None,
                          topics = None,
                          instructions=None,
                          uid=None
                          ):
        

        #data = self.create_default_translation(text, target_language)
        data = {}
        for k, v in locals().iteritems():
            if v is self or v is data: continue
            data[k] = v

        if self.is_bulk:
            self.bulk_data.append(data)
            return

        return self._make_request(data)

    def _build_translation_object(self, json_object):
        source_lang = json_object.get("source_language",None)
        translation = json_object.get("translation",None)
        status = json_object.get("status",None)
            
        translators = [Translator.from_json(t) for t in json_object.get("translators",[])]
            
        translation = Translation(
            uid = json_object["uid"],
            text = json_object["text"],
            target_language = json_object.get('target_language', None),
            source_language = json_object.get('source_lang', None),
            translation = json_object.get('translation', None),
            status = json_object.get('status', None),
            translators = translators,
            topics = json_object.get('topics', None)
        )
        return translation
        

    def _make_request(self, data):
        
        headers={'Authorization': 'ApiKey %s:%s'%(self.username,self.api_key),'content-type': 'application/json'}
        print(data)
        result = requests.post("%stranslation/"% self.api_url, headers=headers, data=json.dumps(data))
        if result.status_code == 201:
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
            raise Exception("Unknown Error return status %d: %s", result.status_code, result.content[0:100])

    def start_bulk_transaction(self):
        self.bulk_data = []
        self.is_bulk = True

    def _post_bulk(self):
        return self._make_request(data=data)

    def post_bulk_translations(self, translations):
        self.start_bulk_transaction()
        for obj in translations:
            obj = copy.deepcopy(obj)
            text, target_language = obj['text'], obj['target_language']
            del obj['text']
            del obj['target_language']
            self.post_translations(text, target_language, **obj)

        self._post_bulk()

    def get_translations(self):
        '''
            Returns the translations requested by the user
        '''
        headers={'Authorization': 'ApiKey %s:%s'%(self.username,self.api_key),'content-type': 'application/json'}
        result = requests.get("%stranslation/"%self.api_url,headers=headers)
        translations_json =  json.loads(result.content)["objects"]
        translations = [Translation(**tj) for tj in translations_json]
        return translations
    


    def get_translation(self,uid):
        '''
            Returns a translation with the given id
        '''
        headers={'Authorization': 'ApiKey %s:%s'%(self.username,self.api_key),'content-type': 'application/json'}
        result = requests.get("%stranslation/%s/"%(self.api_url,uid),headers=headers)
        translation = Translation(**json.loads(result.content))
        return translation
    

    def get_language_pairs(self,train_langs=None):
        '''
            Returns the language pairs available on unbabel
        '''
        headers={'Authorization': 'ApiKey %s:%s'%(self.username,self.api_key),'content-type': 'application/json'}
        if train_langs is None:
            result = requests.get("%slanguage_pair/"%self.api_url,headers=headers)
        else:
            result = requests.get("%slanguage_pair/?train_langs=%s"%(self.api_url,train_langs),headers=headers)
        try:
            logger.debug(result.content)
            langs_json =  json.loads(result.content)
            languages = [LangPair(Language(shortname=lang_json["lang_pair"]["source_language"]["shortname"],
                                       name=lang_json["lang_pair"]["source_language"]["name"]),
                              Language(shortname=lang_json["lang_pair"]["target_language"]["shortname"],
                                       name=lang_json["lang_pair"]["target_language"]["name"])
                              ) for lang_json in langs_json["objects"]]
        except:
            logger.exception("Error decoding get language pairs")
            languages = []
        return languages
    
    def get_tones(self):
        '''
            Returns the tones available on unbabel
        '''
        headers={'Authorization': 'ApiKey %s:%s'%(self.username,self.api_key),'content-type': 'application/json'}
        result = requests.get("%stone/"%self.api_url,headers=headers)
        tones_json =  json.loads(result.content)
        tones = [Tone(name=tone_json["tone"]["name"],
                      description=tone_json["tone"]["description"]) 
                 for tone_json in tones_json["objects"]]
        return tones
    
    def get_topics(self):
        '''
            Returns the topics available on unbabel
        '''
        headers={'Authorization': 'ApiKey %s:%s'%(self.username,self.api_key),'content-type': 'application/json'}
        result = requests.get("%stopic/"%self.api_url,headers=headers)
        topics_json =  json.loads(result.content)
        topics = [Topic(name=tone_json["topic"]["name"]) 
                 for tone_json in topics_json["objects"]]
        return topics
