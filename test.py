from db import SQLite

db = SQLite('db.db')

homework = db.get_user_notification()

for i in homework:
    print(i[0])