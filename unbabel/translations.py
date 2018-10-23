"""Pythonic objects to hold the translation responses from JSON."""

class Translation(object):
    def __init__(
            self,
            uid=-1,
            text="",
            translatedText=None,
            target_language="",
            source_language=None,
            status=None,
            translators=[],
            topics=None,
            price=None,
            text_format='text',
            origin=None,
            price_plan=None,
            balance=None,
            client=None,
            order_number=None):
        self.uid = uid
        self.text = text
        self.translation = translatedText
        self.source_language = source_language
        self.target_language = target_language
        self.status = status
        self.translators = translators
        self.topics = topics
        self.price = price
        self.text_format = text_format
        self.origin = origin
        self.price_plan = price_plan
        self.client = client
        self.balance = balance
        self.order_number = order_number

    def __repr__(self):
        return "{} {} {}_{}".format(
            self.uid, self.status, self.source_language, self.target_language)

    def __str__(self):
        return "{} {} {}_{}".format(
            self.uid, self.status, self.source_language, self.target_language)


class MTTranslation(object):
    def __init__(
            self,
            uid=-1,
            text="",
            translatedText=None,
            target_language="",
            source_language=None,
            status=None,
            topics=None,
            text_format='text',
            origin=None,
            client=None):
        self.uid = uid
        self.text = text
        self.translation = translatedText
        self.source_language = source_language
        self.target_language = target_language
        self.status = status
        self.topics = topics
        self.text_format = text_format
        self.origin = origin
        self.client = client

    def __repr__(self):
        return "{} {} {}_{}".format(
            self.uid, self.status, self.source_language, self.target_language)

    def __str__(self):
        return "{} {} {}_{}".format(
            self.uid, self.status, self.source_language, self.target_language)
