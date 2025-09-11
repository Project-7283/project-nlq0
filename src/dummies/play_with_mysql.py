import json
from ..services.db_reader import DBSchemaReaderService
import os
import dotenv
from ..services.mysql_service import MySQLService
dotenv.load_dotenv()

database=os.getenv("MYSQL_DATABASE")

dbserv=MySQLService()
dbreader = DBSchemaReaderService(dbserv)

# print(dbreader.get_databases())

# databases = dbreader.get_databases()

# for db in databases:
#     tables, views = dbreader.get_tables(db)

#     print(f"\n{db}\n------------------------------\nTables:\n")
#     for table in tables:
#         print(table)

#     print("\nViews:\n")
#     for viw in views:
#         print(viw)

print(json.dumps(dbreader.read_full_schema(), indent=3))
