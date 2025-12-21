import os
import json
import time
from pathlib import Path
from src.modules.semantic_graph import SemanticGraph
from typing import Protocol, Any, List, Dict, Optional
from src.utils.logging import performance_logger

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
        
        # Setup debug logging
        self.debug_log_dir = Path("logs/graph_debug")
        self.debug_log_dir.mkdir(parents=True, exist_ok=True)
        self.enable_debug_dumps = os.getenv("ENABLE_DEBUG_DUMPS", "true").lower() == "true"
    
    def _dump_debug_data(self, filename: str, data: Any, description: str = ""):
        """Dump data to file for debugging"""
        if not self.enable_debug_dumps:
            return
        
        try:
            filepath = self.debug_log_dir / filename
            with open(filepath, 'w') as f:
                if description:
                    f.write(f"# {description}\n\n")
                json.dump(data, f, indent=2, default=str)
            print(f"  🐛 Graph debug dump: {filepath}")
        except Exception as e:
            print(f"  Warning: Could not write graph debug dump {filename}: {e}")

    def build_graph(self, enable_profiling: bool = True):
        """
        Build the semantic graph from database schema.
        Optionally enriches with profiling data if profiling_service is available.
        
        Args:
            enable_profiling: Whether to run profiling for enriched metadata
        """
        start_time = time.time()
        print(f"\n{'='*60}")
        print(f"🏗️  Building semantic graph for database: {self.dbname}")
        print(f"   Profiling enabled: {enable_profiling}")
        print(f"{'='*60}\n")
        
        # Get profiling data if enabled
        profile_data = None
        if enable_profiling and self.profiling_service:
            print("\n🔍 Running database profiling for enriched metadata...")
            try:
                profile_data = self.profiling_service.profile_database(self.dbname)
                print(f"✅ Profiling complete. Tables profiled: {len(profile_data.get('tables', {}))}")
                self._dump_debug_data(
                    "01_profile_data_full.json",
                    profile_data,
                    "Complete profiling data from DBProfilingService"
                )
            except Exception as e:
                print(f"⚠️  Profiling failed, continuing with schema only: {e}")
                profile_data = None
        
        tables, views = self.db_reader.get_tables(self.dbname)
        print(f"\n📋 Retrieved {len(tables)} tables and {len(views)} views from database")
        
        # Add table and attribute nodes with enriched metadata
        print("\n📦 Adding table nodes to graph...")
        for i, table in enumerate(tables, 1):
            print(f"\n[{i}/{len(tables)}] Processing table: {table}")
            
            # Get profiling data for this table
            table_props = {}
            if profile_data and table in profile_data.get("tables", {}):
                table_props = profile_data["tables"][table].get("properties", {})
            
            # Add table node
            self.graph.add_node(table, node_type="table", properties=table_props)
            
            # Get columns for this table
            columns = self.db_reader.get_table_schema(self.dbname, table)
            for col in columns:
                col_name = col.get("Field")
                col_id = f"{table}.{col_name}"
                
                # Get profiling data for this column
                col_props = dict(col)
                if profile_data and table in profile_data.get("tables", {}):
                    col_profile = profile_data["tables"][table].get("columns", {}).get(col_name, {})
                    if col_profile:
                        col_props.update(col_profile.get("properties", {}))
                
                # Add attribute node and association edge
                self.graph.add_node(col_id, node_type="attribute", properties=col_props)
                self.graph.add_edge(table, col_id, condition="association")
        
        # Add view nodes
        print("\n🖼️  Adding view nodes to graph...")
        for view in views:
            self.graph.add_node(view, node_type="view")
            columns = self.db_reader.get_view_schema(self.dbname, view)
            for col in columns:
                col_name = col.get("Field")
                col_id = f"{view}.{col_name}"
                self.graph.add_node(col_id, node_type="attribute", properties=dict(col))
                self.graph.add_edge(view, col_id, condition="association")
        
        # Add foreign key edges
        print("\n🔗 Adding foreign key relationships...")
        # This part depends on how db_reader provides FK info. 
        # For now, we'll assume it's handled or we can add a basic heuristic.
        
        duration = time.time() - start_time
        performance_logger.info(f"Graph generation for {self.dbname} completed in {duration:.2f}s")
        print(f"\n✅ Graph building complete in {duration:.2f}s")
        return self.graph
                table_profile = profile_data["tables"][table]
                print(f"  ✓ Found profiling data for {table}")
                print(f"    Keys in profile: {list(table_profile.keys())}")
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
                    print(f"    Properties extracted: {list(table_props.keys())}")
            else:
                print(f"  ⚠️  No profiling data found for {table}")
            
            self.graph.add_node(table, node_type="table", properties=table_props)
            print(f"  ✓ Added table node: {table}")
            
            # Add columns with enriched metadata
            print(f"\n  📊 Processing columns for table: {table}")
            columns = self.db_reader.get_table_schema(self.dbname, table)
            print(f"    Retrieved {len(columns)} columns from schema")
            print(f"    Column names: {[col['Field'] for col in columns]}")
            
            self._dump_debug_data(
                f"{table}_columns_from_schema.json",
                columns,
                f"Columns retrieved from schema for {table}"
            )
            
            for j, col in enumerate(columns, 1):
                col_node = f"{table}.{col['Field']}"
                col_props = col.copy()  # Start with schema info
                print(f"    [{j}/{len(columns)}] Processing column: {col['Field']}")
                
                # Add profiling data if available
                if profile_data and table in profile_data.get("tables", {}):
                    table_profile = profile_data["tables"][table]
                    if "error" not in table_profile:
                        # Check what's in the profile
                        has_col_stats = col['Field'] in table_profile.get("column_statistics", {})
                        has_col_desc = col['Field'] in table_profile.get("column_descriptions", {})
                        print(f"      - Has stats: {has_col_stats}, Has desc: {has_col_desc}")
                        
                        # Add statistical data
                        col_stats = table_profile.get("column_statistics", {}).get(col['Field'], {})
                        if col_stats:
                            print(f"      - Adding stats: {list(col_stats.keys())}")
                            col_props.update(col_stats)
                        
                        # Add LLM-generated descriptions
                        col_desc = table_profile.get("column_descriptions", {}).get(col['Field'], {})
                        if col_desc:
                            print(f"      - Adding descriptions: {list(col_desc.keys())}")
                            col_props.update(col_desc)
                
                print(f"      - Final properties keys: {list(col_props.keys())}")
                self.graph.add_node(col_node, node_type="attribute", properties=col_props)
                self.graph.add_edge(col_node, table, weight=1.0, condition="association")
                self.graph.add_edge(table, col_node, weight=1.0, condition="association")
                print(f"      ✓ Added column node: {col_node}")
        
        # Add existing view nodes
        print(f"\n👁️  Adding {len(views)} view nodes to graph...")
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
            print(f"  ✓ Added view node: {view}")
        
        # Add virtual tables (LLM-inferred views)
        if profile_data and "virtual_tables" in profile_data:
            print(f"\n✨ Adding {len(profile_data['virtual_tables'])} virtual table nodes...")
            for vt_name, vt_data in profile_data["virtual_tables"].items():
                self.graph.add_node(vt_name, node_type="virtual_table", properties=vt_data)
                print(f"  ✨ Added virtual table: {vt_name}")
        
        # Add table-to-table foreign key edges
        print(f"\n🔗 Adding foreign key edges...")
        fk_count = 0
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
                        print(f"  ✓ FK: {table}.{col['Field']} -> {ref_table}.{ref_col}")
                        fk_count += 1
        
        # Summary
        print(f"\n🎉 Graph build complete!")

    def add_reverse_foreign_keys(self):
        # Add reverse foreign key edges for bidirectional traversal
        self.graph.grow_reverse_edges(condition_filter="foreign_key", new_condition="reverse_foreign_key")

    def save(self):
        os.makedirs(self.output_dir, exist_ok=True)
        out_path = os.path.join(self.output_dir, f"{self.dbname}.json")
        print(f"\n💾 Saving graph to: {out_path}")
        self.graph.save_to_json(out_path)
        print(f"✅ Graph saved successfully!")
        return out_path

    def build_and_save(self, add_reverse_fks=True, enable_profiling=True):
        """
        Build and save the semantic graph.
        
        Args:
            add_reverse_fks: Whether to add reverse foreign key edges
            enable_profiling: Whether to run profiling for enriched metadata
        """
        self.build_graph(enable_profiling=enable_profiling)
        if add_reverse_fks:
            self.add_reverse_foreign_keys()
        return self.save()

