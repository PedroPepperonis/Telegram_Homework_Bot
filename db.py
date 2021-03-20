import os
import psycopg2

class DataBase:

    def __init__(self, database):
        self.connection = psycopg2.connect(database, sslmode='require')
        self.cursor = self.connection.cursor()
    
    def add_homework(self, date, task):
        with self.connection:
            return self.cursor.execute("INSERT INTO Homeworks(date, task) VALUES (%s, %s)", (date, task))
    
    def update_homework(self, date, task):
        with self.connection:
            return self.cursor.execute("UPDATE Homeworks SET task = %s WHERE date = %s", (task, date))

    def get_homework(self, date):
        with self.connection:
            self.cursor.execute("SELECT * FROM Homeworks WHERE date = %s", (date, ))
            return self.cursor.fetchall()

    def get_subscription_status(self, user_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM Subscriptions WHERE user_id = %s", (user_id, ))
            result = self.cursor.fetchall()
            return bool(len(result))

    def get_status(self, status):
        with self.connection:
            self.cursor.execute("SELECT * FROM Subscriptions WHERE status = %s", (status, ))
            return self.cursor.fetchall()

    def get_notif_time(self, user_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM Subscriptions WHERE user_id = %s", (user_id, ))
            return self.cursor.fetchall()

    def add_subscriber(self, user_id, username, time, status = True):
        with self.connection:
            return self.cursor.execute("INSERT INTO Subscriptions(user_id, username, time, status) VALUES(%s, %s, %s, %s)", (user_id, username, time, status))

    def update_subscription(self, user_id, status):
        with self.connection:
            return self.cursor.execute("UPDATE Subscriptions SET status = %s WHERE user_id = %s", (status, user_id))

    def time(self, user_id, time):
        with self.connection:
            return self.cursor.execute("UPDATE Subscriptions SET time = %s WHERE user_id = %s", (time, user_id))

    def get_group_status(self, status):
        with self.connection:
            self.cursor.execute("SELECT * FROM groups WHERE status = %s", (status))
            return self.cursor.fetchall()

    def close(self):
        self.connection.close()
