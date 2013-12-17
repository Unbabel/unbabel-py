Python SDK for the Unbabel REST API


Documentation:
=============

Please visit our documentation page at https://github.com/Unbabel



Installation
============

`pip install unbabel-py`


Getting started:
================

`from unbabel.api import UnbabelApi`

`api = UnbabelApi(username=username,api_key=api_key,api_url="https://www.unbabel.co/tapi/v2/")`

## Request a Translation

`api.post_translations(text="This is a test translation",target_language="en",source_language="pt")`

## Get a Translation

Returns a translation by its uid.

`t = api.get_translation(uid)` 



## Get all Translations

Returns all the translations for a given user.

`api.get_translations()`



## Getting Available Language Pairs 

`api.get_language_pairs()`

> [pt_en,
  pt_fr,
  ... 
  it_en,
  it_fr,
  it_es]
  
  Each element of the list is a **LanguagePair** object that contains a source language and a target language. Each language is an instance of the **Language** class that contains a shortname ( iso639-1 language code ) and a name. 

## Getting Available Tones

`api.get_language_pairs()`

> [Informal, Friendly, Business, Formal]

Each element of the list is a **Tone** object that contains the name and the description of the Tone.
