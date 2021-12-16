
from logging import exception
import json
from typing import Callable, List
from helpers import  todict, wait_until
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import CursorBase
import mysql
import time
import os
import uuid
import mysql.connector
import mysql.connector.pooling
from mysql.connector.pooling import MySQLConnectionPool, PooledMySQLConnection
from threading import Thread
from multiprocessing import Process
from threading import Lock
from config import DATABASES
l = Lock()

sess = str(uuid.uuid4())


class MysqlDatabase:
    
    last_ping: int
    mydb: MySQLConnectionPool
    queued_results: List
    ####
    host: str
    user: str
    password: str
    database: str

    def __init__(self) -> None:
        self.last_ping = 0
        self.mydb = None
        self.queries_queue = []
        self.queued_results = {}
        thread = Thread(target=self._start_connection)
        thread.start()
        # Wait until the database is connected
        wait_until(lambda: bool(self.mydb), timeout=120)
        print('[DatabaseConnected] ', str(bool(self.mydb)), DATABASES['AWS_DASHBOARD']['HOST'])

    def _start_connection(self):
        self.mydb = mysql.connector.connect(
            host=DATABASES['AWS_DASHBOARD']['HOST'],
            user=DATABASES['AWS_DASHBOARD']['USER'],
            password=DATABASES['AWS_DASHBOARD']['PASS'],
            database=DATABASES['AWS_DASHBOARD']['DB'],
            autocommit= True
        )
        self.mydb.autocommit = True



    def query_db(self,query, args=(), one=False):
        cur = self.mydb.cursor()
        cur.execute(query, args)
        r = [dict((cur.description[i][0], value) \
                for i, value in enumerate(row)) for row in cur.fetchall()]
        cur.close()
        return (r[0] if r else None) if one else r


    def cursor(self) -> CursorBase:
        return self.mydb.cursor()
    


    