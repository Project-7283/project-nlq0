import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

class MySQLService:
    def __init__(self, host=None, user=None, password=None, database=None):
        self.db_config = {
            "host": host or os.getenv("MYSQL_HOST"),
            "user": user or os.getenv("MYSQL_USER"),
            "password": password or os.getenv("MYSQL_PASSWORD"),
            "database": database or os.getenv("MYSQL_DATABASE"),
        }

        self.conn = mysql.connector.connect(
        host=self.db_config.get("host"),
        user=self.db_config.get("user"),
        password=self.db_config.get("password"),
        database=self.db_config.get("database"),
        port=3306
        
    )

    def execute_query(self, sql: str, asDict = True):
        cursor = self.conn.cursor(dictionary=asDict)
        cursor.execute(sql)
        if not asDict:
            headers = [ desc[0] for desc in cursor.description ]
        result = cursor.fetchall()

        cursor.close()
        if asDict:
            return result
        else:
            return result, headers
    
    def run_sql(self, sql):
        return self.conn.info_query(sql)
    
    def shutdown(self):
        self.conn.close()
