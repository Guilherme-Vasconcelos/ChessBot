import datetime

import peewee
from bot.orm.db import db


class ExampleModel(peewee.Model):
    example_number_field = peewee.BigIntegerField(null=True, unique=True)
    example_text_field = peewee.TextField()
    created = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
