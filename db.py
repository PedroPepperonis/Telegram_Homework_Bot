import sqlite3

class SQLite:

    def __init__(self, datebase):
        self.connection = sqlite3.connect(datebase)
        self.cursor = self.connection.cursor()

    def add_homework(self, date, task):
        with self.connection:
            return self.cursor.execute("INSERT INTO `dz` (`date`, `task`) VALUES(?, ?)", (date, task))

    def add_message(self, user_id, username, full_name, msg):
        with self.connection:
            return self.cursor.execute("INSERT INTO `msg` (`user_id`, `username`, `full_name`, `msg`) VALUES(?, ?, ?, ?)", (user_id, username, full_name, msg))

    def get_homework(self, date):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `dz` WHERE `date` = ?", (date,)).fetchall()

    def get_status_notifications(self, status = True):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `notifications` WHERE `status` = ?", (status,)).fetchall()

    def add_subscriber(self, user_id, status = True):
        with self.connection:
            return self.cursor.execute("INSERT INTO `notifications` (`user_id`, `status`) VALUES(?, ?)",(user_id, status))

    def get_users_status_notifications(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `notifications` WHERE `user_id` = ? ", (user_id,)).fetchall()
            return bool(len(result))

    def update_subscription(self, user_id, status):
        with self.connection:
            return self.cursor.execute("UPDATE `notifications` SET `status` = ? WHERE `user_id` = ?", (status, user_id))

    def close(self):
        self.connection.close()