import peewee as pw


db = pw.SqliteDatabase('database/bot_db.sqlite3')


class User(pw.Model):
    telegram_id = pw.IntegerField(primary_key=True)
    username = pw.CharField()
    access_token = pw.CharField(null=True)
    refresh_token = pw.CharField(null=True)
    token_expiry = pw.DateTimeField(null=True)

    class Meta:
        database = db
        

async def init_db():
    db.connect()
    db.create_tables([User], safe=True)
    print('init_db')
