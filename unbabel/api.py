'''
Created on Dec 13, 2013

@author: joaograca
'''



import requests
import json



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
                 translation=None,
                 target_language="",
                 source_language=None,
                 status=None,
                 translators=[],
                 topics=None):
        self.uid = uid
        self.text = text
        self.translation = translation
        self.source_language = source_language
        self.target_language = target_language
        self.status = status
        self.translators = translators
        self.topics = topics
    
    def __repr__(self):
        return "%s %s %s_%s"%(self.uid,self.status,self.source_language, self.source_language)
    
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
                          ):
        
        headers={'Authorization': 'ApiKey %s:%s'%(self.username,self.api_key),'content-type': 'application/json'}
        data = {
                "text":text,
                "target_language":target_language
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
        result = requests.post("%stranslation/"%self.api_url,headers=headers,data=json.dumps(data))
        if result.status_code == 201:
            json_object =  json.loads(result.content)
            source_lang = json_object.get("source_language",None)
            translation = json_object.get("translation",None)
            status = json_object.get("status",None)
            
            translators = [Translator.from_json(t) for t in json_object.get("translators",[])]
            
            
            translation = Translation(uid=json_object["uid"],
                                      text = json_object["text"],
                                      target_language = target_language,
                                      source_language = source_lang,
                                      translation = translation,
                                      status=status,
                                      translators=translators,
                                      topics = topics
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
        headers={'Authorization': 'ApiKey %s:%s'%(self.username,self.api_key),'content-type': 'application/json'}
        result = requests.get("%stranslation/"%self.api_url,headers=headers)
        return json.loads(result.content)
    


    def get_translation(self,uid):
        '''
            Returns a translation with the given id
        '''
        headers={'Authorization': 'ApiKey %s:%s'%(self.username,self.api_key),'content-type': 'application/json'}
        result = requests.get("%stranslation/%s/"%(self.api_url,uid),headers=headers)
        return json.loads(result.content)
    

    def get_language_pairs(self):
        '''
            Returns the language pairs available on unbabel
        '''
        headers={'Authorization': 'ApiKey %s:%s'%(self.username,self.api_key),'content-type': 'application/json'}
        result = requests.get("%slanguage_pair/"%self.api_url,headers=headers)
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
