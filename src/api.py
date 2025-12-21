import uvicorn
import json
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from decimal import Decimal
from src.flows.nl_to_sql import process_nl_query_async
from src.utils.logging import app_logger, performance_logger
import time

app = FastAPI(title="NLQ to SQL API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        raise HTTPException(status_code=400, detail="Missing 'query' field")
    
    start_time = time.time()
    app_logger.info(f"Received query request: {nl_query}")
    
    try:
        sql, results = await process_nl_query_async(nl_query)
        
        duration = time.time() - start_time
        performance_logger.info(f"Query processed in {duration:.2f}s | Query: {nl_query[:50]}...")
        
        # Use custom encoder for Decimal
        json_str = json.dumps({"results": results, "sql": sql}, default=decimal_default)
        return JSONResponse(content=json.loads(json_str))
        
    except Exception as e:
        app_logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)
