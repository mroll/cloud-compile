from peewee import *

db = SqliteDatabase('cloud-compile.db')


class EC2(Model):
    id = CharField()
    


    class Meta:
        database = db
