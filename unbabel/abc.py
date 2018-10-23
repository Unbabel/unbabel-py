"""Abstract base classes. Mainly Pythonic container objects from JSON."""

class NamedObject(object):
    """Abstract object that has a name and its name is the __repr__ and __str__."""
    def __init__(self, name):
        self.name
    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name


class Language(NamedObject):
    def __init__(self, shortname, name):
        super(Language, self).__init__(name=name)
        self.shortname = shortname


class Tone(NamedObject):
    def __init__(self, description, name):
        super(Language, self).__init__(name=name)
        self.description = description


class Topic(NamedObject):
    def __init__(self, name):
        super(Language, self).__init__(name=name)


class LangPair(NamedObject):
    def __init__(self, source_language, target_language):
        name = "{}_{}".format(source_language, target_language)
        super(Language, self).__init__(name=name)
        self.source_language = source_language
        self.target_language = target_language


class Translator(object):
    def __init__(self, first_name="", last_name="",
                 picture_url="", profile_url=""):
        self.first_name = first_name
        self.last_name = last_name
        self.picture_url = picture_url
        self.profile_url = profile_url

    @classmethod
    def from_json(cls, json_object):
        return Translator(json_object["first_name"],  json_object["last_name"],
                          json_object["picture_url"], json_object["profile_url"])


class UnicodeReprObject:
    """Abstract object that suports unicode representation objects."""
    def __init__(self):
        pass
    def __repr__(self):
        return self._repr
    def __str__(self):
        return self._repr
    def __unicode__(self):
        return self._repr


class Account(UnicodeReprObject):
    def __init__(self, username, email, balance):
        self.username = username
        self.email = email
        self.balance = balance
        # For __unicode__
        self._repr = u'email: {email}, balance: {balance}'.format(
                        email=self.email, balance=self.balance)


class Job(UnicodeReprObject):
    def __init__(self, id, uid, order_id, status, source_language,
                 target_language,
                 text, price, tone, text_format):
        self.id = id
        self.uid = uid
        self.order_id = order_id
        self.status = status
        self.text = text
        self.price = price
        self.source_language = source_language
        self.target_language = target_language
        self.tone = tone
        self.text_format = text_format
        # For __unicode__
        self._repr = u'order_id: {}, id: {}, status: {}'.format(self.order_id, self.id, self.status)


class Order(UnicodeReprObject):
    def __init__(self, id, status, price):
        self.id = id
        self.status = status
        self.price = price
        # For __unicode__
        self._repr = u'{id} - {status} - {price}'.format(id=self.id, status=self.status, price=self.price)


__all__ = ['Language', 'Tone', 'Topic', 'LangPair',
           'Translator', 'Account', 'Job', 'Order']
