'''
Created on Dec 13, 2013

@author: joaograca
'''



import requests
import json

UNBABEL_API_URL="http://127.0.0.1:8000/tapi/v2/"

## User with money
UNBABEL_USERNAME="gracaninja"
UNBABEL_APIKEY="5a6406e31f77ef779c4024b1579f0f6103944c5e"

##User without money
UNBABEL_USERNAME="gracaninja-1"
UNBABEL_APIKEY="ea7974274e95d99e6f5d84ea92a8ccfcdeba0b4e"




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



class UnbabelApi(object):
    
    def __init__(self, *args, **kwargs):
        object.__init__(self, *args, **kwargs)

    def post_translations(self,text,target_language,
                          source_language=None,
                          type=None,
                          tone=None,
                          visibility=None,
                          public_url=None
                          ):
        
        headers={'Authorization': 'ApiKey %s:%s'%(UNBABEL_USERNAME,UNBABEL_APIKEY),'content-type': 'application/json'}
        data = {
                "text":text,
                "target_language":target_language
                }
        result = requests.post("%stranslation/"%UNBABEL_API_URL,headers=headers,data=json.dumps(data))
        if result.status_code == 201:
            return json.loads(result.content)
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
        headers={'Authorization': 'ApiKey %s:%s'%(UNBABEL_USERNAME,UNBABEL_APIKEY),'content-type': 'application/json'}
        result = requests.get("%stranslation/"%UNBABEL_API_URL,headers=headers)
        return json.loads(result.content)
    
    
    def get_translation(self,id):
        '''
            Returns a translation with the given id
        '''
        headers={'Authorization': 'ApiKey %s:%s'%(UNBABEL_USERNAME,UNBABEL_APIKEY),'content-type': 'application/json'}
        result = requests.get("%stranslation/%s/"%(UNBABEL_API_URL,id),headers=headers)
        return json.loads(result.content)
    

    def get_language_pairs(self):
        '''
            Returns the language pairs available on unbabel
        '''
        headers={'Authorization': 'ApiKey %s:%s'%(UNBABEL_USERNAME,UNBABEL_APIKEY),'content-type': 'application/json'}
        result = requests.get("%slanguage_pair/"%UNBABEL_API_URL,headers=headers)
        return json.loads(result.content)
    
    def get_tones(self):
        '''
            Returns the tones available on unbabel
        '''
        headers={'Authorization': 'ApiKey %s:%s'%(UNBABEL_USERNAME,UNBABEL_APIKEY),'content-type': 'application/json'}
        result = requests.get("%stone/"%UNBABEL_API_URL,headers=headers)
        return json.loads(result.content)
    
    
