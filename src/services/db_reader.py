from .mysql_service import MySQLService

class DBSchemaReaderService:
    def __init__(self, mysql_service: MySQLService):
        self.mysql_service = mysql_service

    def get_databases(self):
        query = "SHOW DATABASES;"
        result, headers = self.mysql_service.execute_query(query, False)
        # print(result)
        return [row[0] for row in result if row[0] not in ('information_schema', 'mysql', 'performance_schema', 'sys')]

    def get_tables(self, database):
        query = f"SHOW FULL TABLES FROM `{database}`"
        result, headers = self.mysql_service.execute_query(query, asDict=False)
        tables = []
        views = []
        print(result)
        for row in result:
            table_name, table_type = row
            if table_type.lower() == 'base table':
                tables.append(table_name)
            elif table_type.lower() == 'view':
                views.append(table_name)
        return tables, views
    
    def get_views(self, database):
        """Get list of views only"""
        tables, views = self.get_tables(database)
        return views

    def get_stored_procedures(self, database):
        query = f"""
            SELECT ROUTINE_NAME 
            FROM information_schema.ROUTINES 
            WHERE ROUTINE_SCHEMA = '{database}' AND ROUTINE_TYPE = 'PROCEDURE'
        """
        result = self.mysql_service.execute_query(query)
        return [row['ROUTINE_NAME'] for row in result]

    def get_table_schema(self, database, table):
        query = f"SHOW FULL COLUMNS FROM `{database}`.`{table}`"
        result = self.mysql_service.execute_query(query)

        return [dict(row) for row in result]

    def get_view_schema(self, database, view):
        query = f"SHOW CREATE VIEW `{database}`.`{view}`"
        result = self.mysql_service.execute_query(query)
        if result:
            return {'Create View': result[0].get('Create View')}
        return {}

    def get_procedure_schema(self, database, procedure):
        query = f"""
            SHOW CREATE PROCEDURE `{database}`.`{procedure}`
        """
        result = self.mysql_service.execute_query(query)
        if result:
            return {'Create Procedure': result[0].get('Create Procedure')}
        return {}

    def read_full_schema(self):
        schema = {}
        databases = self.get_databases()
        for db in databases:
            schema[db] = {
                'tables': {},
                'views': {},
                'procedures': {}
            }
            tables, views = self.get_tables(db)
            for table in tables:
                schema[db]['tables'][table] = self.get_table_schema(db, table)
            for view in views:
                schema[db]['views'][view] = self.get_view_schema(db, view)
            procedures = self.get_stored_procedures(db)
            for proc in procedures:
                schema[db]['procedures'][proc] = self.get_procedure_schema(db, proc)
        return schema