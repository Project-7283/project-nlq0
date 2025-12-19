import os
from src.modules.semantic_graph import SemanticGraph
from typing import Protocol, Any, List, Dict, Optional

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
    Now supports enrichment with DBProfilingService for semantic metadata.
    """

    def __init__(
        self, 
        db_reader: DBReaderProtocol, 
        dbname: str, 
        output_dir: str = "schemas",
        profiling_service: Optional[Any] = None
    ):
        """
        db_reader: An object with methods get_tables(dbname), get_table_schema(dbname, table), get_views(dbname), get_view_schema(dbname, view)
        dbname: Name of the database
        output_dir: Directory to save the graph JSON
        profiling_service: Optional DBProfilingService for enriched metadata
        """
        self.db_reader = db_reader
        self.dbname = dbname
        self.output_dir = output_dir
        self.profiling_service = profiling_service
        self.graph = SemanticGraph()

    def build_graph(self, enable_profiling: bool = True):
        """
        Build the semantic graph from database schema.
        Optionally enriches with profiling data if profiling_service is available.
        
        Args:
            enable_profiling: Whether to run profiling for enriched metadata
        """
        # Get profiling data if enabled
        profile_data = None
        if enable_profiling and self.profiling_service:
            print("\n🔍 Running database profiling for enriched metadata...")
            try:
                profile_data = self.profiling_service.profile_database(self.dbname)
            except Exception as e:
                print(f"⚠️  Profiling failed, continuing with schema only: {e}")
                profile_data = None
        
        tables, views = self.db_reader.get_tables(self.dbname)
        
        # Add table and attribute nodes with enriched metadata
        for table in tables:
            # Get profiling data for this table
            table_props = {}
            if profile_data and table in profile_data.get("tables", {}):
                table_profile = profile_data["tables"][table]
                if "error" not in table_profile:
                    table_props = {
                        "row_count": table_profile.get("row_count"),
                        "business_purpose": table_profile.get("business_purpose"),
                        "data_domain": table_profile.get("data_domain"),
                        "business_impact": table_profile.get("business_impact"),
                        "description": table_profile.get("description"),
                        "typical_queries": table_profile.get("typical_queries", []),
                        "related_business_processes": table_profile.get("related_business_processes", []),
                        "table_comment": table_profile.get("table_comment", "")
                    }
            
            self.graph.add_node(table, node_type="table", properties=table_props)
            
            # Add columns with enriched metadata
            columns = self.db_reader.get_table_schema(self.dbname, table)
            for col in columns:
                col_node = f"{table}.{col['Field']}"
                col_props = col.copy()  # Start with schema info
                
                # Add profiling data if available
                if profile_data and table in profile_data.get("tables", {}):
                    table_profile = profile_data["tables"][table]
                    if "error" not in table_profile:
                        # Add statistical data
                        col_stats = table_profile, enable_profiling=True):
        """
        Build and save the semantic graph.
        
        Args:
            add_reverse_fks: Whether to add reverse foreign key edges
            enable_profiling: Whether to run profiling for enriched metadata
            
        Returns:
            Path to saved graph JSON file
        """
        self.build_graph(enable_profiling=enable_profilingol_props.update(col_stats)
                        
                        # Add LLM-generated descriptions
                        col_desc = table_profile.get("column_descriptions", {}).get(col['Field'], {})
                        col_props.update(col_desc)
                
                self.graph.add_node(col_node, node_type="attribute", properties=col_props)
                self.graph.add_edge(col_node, table, weight=1.0, condition="association")
                self.graph.add_edge(table, col_node, weight=1.0, condition="association")
        
        # Add existing view nodes
        for view in views:
            view_props = {}
            if profile_data and view in profile_data.get("views", {}):
                view_profile = profile_data["views"][view]
                view_props = {
                    "description": view_profile.get("description", ""),
                    "view_comment": view_profile.get("view_comment", ""),
                    "create_statement": view_profile.get("create_statement", "")
                }
            self.graph.add_node(view, node_type="view", properties=view_props)
        
        # Add virtual tables (LLM-inferred views)
        if profile_data and "virtual_tables" in profile_data:
            for vt_name, vt_data in profile_data["virtual_tables"].items():
                self.graph.add_node(vt_name, node_type="virtual_table", properties=vt_data)
                print(f"  ✨ Added virtual table: {vt_name}")
        
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
