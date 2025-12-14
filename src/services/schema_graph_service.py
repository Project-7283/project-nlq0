import os
from src.modules.semantic_graph import SemanticGraph
from typing import Protocol, Any, List, Dict

class DBReaderProtocol(Protocol):
    def get_tables(self, dbname: str) -> list[str]: ...
    def get_table_schema(self, dbname: str, table: str) -> List[Dict[str, Any]]: ...
    def get_views(self, dbname: str) -> list[str]: ...
    def get_view_schema(self, dbname: str, view: str) -> List[Dict[str, Any]]: ...
    @property
    def mysql_service(self) -> Any: ...

class SchemaGraphService:
    """
    Generic service to extract a database schema and create a semantic graph.
    Can be used in any workflow (e.g., LangGraph) for schema-driven reasoning.
    """

    def __init__(self, db_reader: DBReaderProtocol, dbname: str, output_dir: str = "schemas"):
        """
        db_reader: An object with methods get_tables(dbname), get_table_schema(dbname, table), get_views(dbname), get_view_schema(dbname, view)
        dbname: Name of the database
        output_dir: Directory to save the graph JSON
        """
        self.db_reader = db_reader
        self.dbname = dbname
        self.output_dir = output_dir
        self.graph = SemanticGraph()

    def build_graph(self):
        tables, views = self.db_reader.get_tables(self.dbname)
        # Add table and attribute nodes
        for table in tables:
            self.graph.add_node(table, node_type="table")
            columns = self.db_reader.get_table_schema(self.dbname, table)
            for col in columns:
                col_node = f"{table}.{col['Field']}"
                self.graph.add_node(col_node, node_type="attribute", properties=col)
                self.graph.add_edge(col_node, table, weight=1.0, condition="association")
                self.graph.add_edge(table, col_node, weight=1.0, condition="association")
        # Add view nodes (optional, can be extended)
        for view in views:
            self.graph.add_node(view, node_type="view")
            # Optionally, parse columns from view definition
        # Add table-to-table foreign key edges
        for table in tables:
            columns = self.db_reader.get_table_schema(self.dbname, table)
            for col in columns:
                if col.get('Key') == 'MUL':
                    fk_query = f"""
                        SELECT REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                        FROM information_schema.KEY_COLUMN_USAGE
                        WHERE TABLE_SCHEMA = '{self.dbname}' AND TABLE_NAME = '{table}' AND COLUMN_NAME = '{col['Field']}'
                            AND REFERENCED_TABLE_NAME IS NOT NULL
                    """
                    fk_result = self.db_reader.mysql_service.execute_query(fk_query)
                    for fk in fk_result:
                        ref_table = fk['REFERENCED_TABLE_NAME']
                        ref_col = fk['REFERENCED_COLUMN_NAME']
                        self.graph.add_edge(
                            table,
                            ref_table,
                            weight=0.2,
                            condition="foreign_key",
                            properties={
                                "source_attribute": f"{table}.{col['Field']}",
                                "destination_attribute": f"{ref_table}.{ref_col}"
                            }
                        )

    def add_reverse_foreign_keys(self):
        # Add reverse foreign key edges for bidirectional traversal
        self.graph.grow_reverse_edges(condition_filter="foreign_key", new_condition="reverse_foreign_key")

    def save(self):
        os.makedirs(self.output_dir, exist_ok=True)
        out_path = os.path.join(self.output_dir, f"{self.dbname}.json")
        self.graph.save_to_json(out_path)
        return out_path

    def build_and_save(self, add_reverse_fks=True):
        self.build_graph()
        if add_reverse_fks:
            self.add_reverse_foreign_keys()
        return self.save()
