from mongoengine import *

class Article(Document):
    artId = IntField(required=True)
    name = StringField(max_length=20)
    case = StringField()
    content = StringField()


class LawChapter(Document):
    chapterId=IntField(required=True)
    name = StringField(max_length=20)
    articles = ListField(ReferenceField(Article))

class LawTitle(Document):
    titleId = IntField(required=True)
    name = StringField(max_length=20)
    chapters = ListField(ReferenceField(LawChapter))

class LawPart(Document):
    partId = IntField(required=True)
    name = StringField(max_length=20)
    type = IntField()
    titles = ListField(ReferenceField(LawTitle))

class LawDocument(Document):
    name = StringField(max_length=20)
    parts = ListField(ReferenceField(LawPart))