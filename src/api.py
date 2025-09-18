
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.flows.nl_to_sql import process_nl_query
import json
from decimal import Decimal


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

@app.post("/query")
async def query_endpoint(request: Request):
    data = await request.json()
    nl_query = data.get("query")
    if not nl_query:
        return JSONResponse({"error": "Missing 'query' field"}, status_code=400)
    try:
        sql, results = process_nl_query(nl_query)
        # sql, results = "dummy sql", [{ 'col1': 'value1' }, {'col1': 'value2'}, { 'col1': 'value1' }, {'col1': 'value2'}]
        # Use custom encoder for Decimal
        json_str = json.dumps({"results": results, "sql": sql}, default=decimal_default)
        return JSONResponse(content=json.loads(json_str))
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)
