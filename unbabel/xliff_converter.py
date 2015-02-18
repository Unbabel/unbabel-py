__author__ = 'joaograca'

from bs4 import BeautifulSoup

def generate_xliff(entry_dict):
    """
    Given a dictionary with keys = ids
    and values equals to strings generates
    and xliff file to send to unbabel.

    Example:
    {"123": "This is blue car",
     "234": "This house is yellow"
     }

     returns
     <xliff version = "1.2">
          <file original = "" source-language = "en" target-language = "fr">
           <head> </ head>
      <body>
      <trans-unit id = "14077">
      <source> T2 apartment, as new building with swimming pool, sauna and gym. Inserted in Quinta da Beloura 1, which offers a variety of services such as private security 24 hours, tennis, golf, hotel, restaurants, and more. The apartment has air conditioning in all rooms, central heating, balcony and security screen for children in all windows.
    </ source>
       </ trans-unit>
      </ body>
      </ file>
      </ xliff>

    """
    entries = ""
    for key,value in entry_dict.iteritems():
        entries+=create_trans_unit(key,value).strip()+"\n"
    xliff_str = get_head_xliff().strip()+"\n"+entries+get_tail_xliff().strip()
    return xliff_str

def get_head_xliff():
    return '''
<xliff version = "1.2">
<file original = "" source-language = "" target-language = "">
<head> </head>
<body>
    '''
def get_tail_xliff():
    return '''
</body>
</file>
</xliff>
    '''

def create_trans_unit(key, value):
    return '''
<trans-unit id="%s">
    <source>
        %s
    </source>
</trans-unit>
           '''%(key,value)

def get_dictionary_from_xliff(xliff_text,side="target"):
    soup = BeautifulSoup(xliff_text)
    trans_units = soup.find_all("trans-unit")
    result_dic = {}
    for trans_unit in trans_units:
        _id = trans_unit["id"]
        if side == "target":
            result_dic[_id] = trans_unit.target.text.strip()
        else:
            result_dic[_id] = trans_unit.source.text.strip()
    return result_dic