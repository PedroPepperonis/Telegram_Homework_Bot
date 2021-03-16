from db import SQLite

db = SQLite('db.db')

date = input("Дата: ")
task = input("Задание: ")

db.add_homework(date, task)

print("Задание добавлено")