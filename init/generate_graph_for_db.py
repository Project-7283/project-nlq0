import os
from src.services.mysql_service import MySQLService
from src.services.db_reader import DBSchemaReaderService
from src.modules.semantic_graph import SemanticGraph

# filepath: generate_graph_for_db.py


def main():
    # Optionally, grow reverse foreign key edges for SQL traversal
    def grow_reverse_foreign_keys_sql(graph):
        # Only add reverse for table-to-table foreign_key edges
        graph.grow_reverse_edges(condition_filter="foreign_key", new_condition="foreign_key")

    # Initialize MySQLService (reads credentials from .env or config)
    mysql_service = MySQLService()
    db_reader = DBSchemaReaderService(mysql_service)
    graph = SemanticGraph()

    dbname = "ecommerce_marketplace"

    # Fetch tables and views
    tables, views = db_reader.get_tables(dbname)

    # Add table nodes and their columns as attribute nodes (association only)
    for table in tables:
        graph.add_node(table, node_type="table")
        columns = db_reader.get_table_schema(dbname, table)
        for col in columns:
            col_node = f"{table}.{col['Field']}"
            graph.add_node(col_node, node_type="attribute", properties=col)
            # Only association: attribute <-> table
            graph.add_edge(col_node, table, weight=1.0, condition="association")
            graph.add_edge(table, col_node, weight=1.0, condition="association")

    # Add view nodes
    for view in views:
        graph.add_node(view, node_type="view")
        view_schema = db_reader.get_view_schema(dbname, view)
        # Optionally, parse view_schema['Create View'] for columns

    # Add table-to-table foreign key relationships as edges with metadata
    for table in tables:
        columns = db_reader.get_table_schema(dbname, table)
        for col in columns:
            if col.get('Key') == 'MUL':
                fk_query = f"""
                    SELECT REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                    FROM information_schema.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = '{dbname}' AND TABLE_NAME = '{table}' AND COLUMN_NAME = '{col['Field']}'
                        AND REFERENCED_TABLE_NAME IS NOT NULL
                """
                fk_result = mysql_service.execute_query(fk_query)
                for fk in fk_result:
                    ref_table = fk['REFERENCED_TABLE_NAME']
                    ref_col = fk['REFERENCED_COLUMN_NAME']
                    # Edge: table -> referenced table, with FK metadata
                    graph.add_edge(
                        table,
                        ref_table,
                        weight=0.2,
                        condition="foreign_key",
                        properties={
                            "source_attribute": f"{table}.{col['Field']}",
                            "destination_attribute": f"{ref_table}.{ref_col}"
                        }
                    )

    # Save graph to schemas/<dbname>.json
    os.makedirs("schemas", exist_ok=True)
    out_path = f"schemas/{dbname}.json"
    # Add reverse foreign key edges if needed
    grow_reverse_foreign_keys_sql(graph)
    graph.save_to_json(out_path)

if __name__ == "__main__":
    main()