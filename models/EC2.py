from peewee import *
from playhouse.fields import ManyToManyField

db = SqliteDatabase('cloud-compile.db')

class EC2(Model):
    id = CharField()
    groupSet = ManyToManyField(ScurityGroup, backref='ec2s')


    class Meta:
        database = db
