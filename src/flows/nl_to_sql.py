from models.llm import generate_sql
from services.mysql_service import execute_sql
from services.vector_service import retrieve_context


def process_nl_query(nl_query: str):
    context = retrieve_context(nl_query)
    sql = generate_sql(nl_query, context)
    result = 'didnot run it' #execute_sql(sql)
    return sql, result
