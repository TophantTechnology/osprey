import datetime
import json
import sqlite3
from copy import deepcopy
from pymongo import MongoClient
from lib.log import logger as log
from settings import use_mongo, use_sqlite, mongo_url, mongo_db_name, mongo_task_coll, mongo_resp_coll, mongo_basic_coll, sqlite_path


class MongoDB:
    def __init__(self, url, db_name):
        try:
            self.client = MongoClient(url,connect=False, socketTimeoutMS=300, connectTimeoutMS=300,
                                         serverSelectionTimeoutMS=300)
            self.db_name = db_name
        except Exception as e:
            log.error(e)

    def check_connection(self):
        try:
            self.db_client = self.client.get_database(self.db_name)
            return True
        except Exception as e:
            log.error("Failed to connect to mongodb. {}".format(e))
            return False

    def insert_data(self, collection, data):
        try:
            self.db_client[collection].insert_one(data)
            return True
        except Exception as e:
            log.error("Failed to insert data to mongodb. {}".format(e))
            return False

    def update(self, collection, filter, updates):
        try:
            self.db_client[collection].update_one(filter, {"$set": updates})
            return True
        except Exception as e:
            log.error("Failed to update data in mongodb. {}".format(e))
            return False

    def find_one(self, collection, filter):
        try:
            return self.db_client[collection].find_one(filter)
        except Exception as e:
            log.error("Failed to find data in mongodb. {}".format(e))
            return None

    def find(self, collection, filter):
        try:
            return self.db_client[collection].find(filter)
        except Exception as e:
            log.error("Failed to find data in mongodb. {}".format(e))
            return None


class SqliteDB:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_cursor(self):
        try:
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()
            return cursor, connection
        except Exception as e:
            log.error("Failed to connect to SQLite. {}".format(e))
            return None

    def table_check(self):
        try:
            cursor, connection = self.get_cursor()
        except TypeError:
            return False
        try:
            tables = ["".join(t) for t in cursor.execute('''SELECT name FROM sqlite_master WHERE type='table';''')]
            if "task" not in tables:
                cursor.execute('''CREATE TABLE task(date TEXT, taskID TEXT, data TEXT)''')
            if "session" not in tables:
                cursor.execute('''CREATE TABLE session(date TEXT, sessionName TEXT, taskIDs TEXT)''')
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            log.error("Table check failed in sqlite. {}".format(e))
            return False

    def _get_datetime(self):
        today = datetime.date.today()
        time = today.ctime()
        return time

    def create_task(self, task_id, data=""):
        try:
            cursor, connection = self.get_cursor()
        except TypeError:
            return False
        try:
            cursor.execute("""INSERT INTO task VALUES (?, ?, ?)""", (self._get_datetime(), task_id, data))
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            log.error("Failed to create task in sqlite. {}".format(e))
            return False

    def save_result(self, task_id, data):
        try:
            cursor, connection = self.get_cursor()
        except TypeError:
            return False
        try:
            data = json.dumps(data)
            cursor.execute("""UPDATE task SET data = ? WHERE taskID = ?""", (data, task_id))
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            log.error("Failed to save result in sqlite. {}".format(e))
            return False

    def get_result(self, task_id):
        try:
            cursor, connection = self.get_cursor()
        except TypeError:
            return False
        try:
            cursor.execute("""SELECT data FROM task WHERE taskID = ? """, (task_id,))
            result = cursor.fetchall()[0][0]
            connection.close()
            return result
        except Exception as e:
            log.error("Failed to get result in sqlite. {}".format(e))
            return None


class DBClient:
    def __init__(self, use_mongodb=use_mongo, use_sqlite=use_sqlite):
        self.use_sqlite = self.use_mongodb = False
        if use_mongodb and mongo_url and mongo_db_name and mongo_task_coll and mongo_resp_coll:
            self.mongo = MongoDB(mongo_url, mongo_db_name)
            self.use_mongodb = self.mongo.check_connection()
            self.mongo_task_collection = mongo_task_coll
            self.mongo_resp_collection = mongo_resp_coll
            self.mongo_basic_collection = mongo_basic_coll
        if use_sqlite and sqlite_path:
            self.sqlite = SqliteDB(sqlite_path)
            if self.sqlite.get_cursor():
                self.use_sqlite = True
                self.sqlite.table_check()

    def create_task(self, task_id, start_time):
        if self.use_sqlite:
            self.sqlite.create_task(task_id=task_id, data="Have Submitted Task, Please Wait.")
        if self.use_mongodb:
            self.mongo.insert_data(self.mongo_task_collection, {"task_id": task_id,
                                                                "data": "Have Submitted Task, Please Wait.",
                                                                "start_time": start_time})

    def create_basic(self, task_id, mode, start_time, targets, vids):
        if self.use_mongodb:
            info = {"task_id": task_id, "start_time": start_time,
                    "poc_id": vids, "target": targets,
                    "mode": 2 if mode.strip() == "exploit" else 1}
            self.mongo.insert_data(self.mongo_basic_collection, info)

    def save_result(self, task_id, data, end_time):
        if self.use_sqlite:
            self.sqlite.save_result(task_id=task_id, data=data)
        if self.use_mongodb:
            self.mongo.update(self.mongo_task_collection, {"task_id": task_id}, {"data": data, "end_time": end_time})

    def save_basic(self, task_id, end_time):
        if self.use_mongodb:
            self.mongo.update(self.mongo_basic_collection, {"task_id": task_id}, {"end_time": end_time})

    def get_result(self, task_id):
        """使用mongodb时，取返回结果的data键值, 使用sqlite时，直接取返回结果"""
        if self.use_mongodb:
            return self.mongo.find_one(self.mongo_task_collection, {"task_id": task_id})
        if self.use_sqlite:
            return json.loads(self.sqlite.get_result(task_id=task_id))

    def get_specify_results(self, filter):
        if self.use_mongodb:
            return self.mongo.find(self.mongo_task_collection, filter)
        if self.use_sqlite:
            pass

    def save_response(self, filter, response):
        if self.use_mongodb:
            origin = self.get_response(filter)
            if not origin:
                filter.update({"response": [response]})
                self.mongo.insert_data(self.mongo_resp_collection, filter)
            else:
                data = deepcopy(filter)
                origin.get("response").extend([response])
                data.update({"response": origin.get("response")})
                self.mongo.update(self.mongo_resp_collection, filter, data)
        if self.use_sqlite:
            pass

    def get_response(self, filters):
        if self.use_mongodb:
            return self.mongo.find_one(self.mongo_resp_collection, filters)
        if self.use_sqlite:
            pass
