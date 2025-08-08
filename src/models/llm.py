import os
import json
import logging
import requests
from dotenv import load_dotenv
from langchain_community.llms import Ollama, OpenAI
from langchain.prompts import PromptTemplate

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def generate_sql(nl_query: str, context: str) -> str:
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        logging.info("Using Gemini API for SQL generation")
        
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        headers = {
            "Content-Type": "application/json"
        }
        
        request_body = {
            "contents": [{
                "parts": [{
                    "text": f"""You are an expert SQL query generator. Generate SQL queries from natural language.
                    Given this context: {context}
                    Generate SQL for this query: {nl_query}
                    
                    Respond ONLY with a valid JSON object in this format:
                    {{
                        "sql": "the SQL query",
                        "explanation": "brief explanation of what the query does"
                    }}"""
                }]
            }]
        }
        
        logging.debug(f"Sending request to Gemini API: {json.dumps(request_body, indent=2)}")
        
        response = requests.post(
            url,
            headers=headers,
            params={"key": gemini_api_key},
            json=request_body
        )
        
        logging.debug(f"Response status: {response.status_code}")
        logging.debug(f"Full response: {json.dumps(response.json(), indent=2)}")
        
        logging.debug(f"Received response from Gemini API: {response.text}")
        
        try:
            if response.status_code == 200:
                # Extract the text from Gemini's response structure
                content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                logging.debug(f"Extracted content: {content}")
                
                # Parse the JSON from the response text
                result = json.loads(content)
                logging.info("Successfully parsed JSON response")
                logging.debug(f"Parsed result: {json.dumps(result, indent=2)}")
                
                return f"SQL: {result['sql']}\nExplanation: {result['explanation']}"
            else:
                error_msg = f"API error: {response.status_code} - {response.text}"
                logging.error(error_msg)
                return error_msg
        except Exception as e:
            logging.error(f"Error parsing response: {str(e)}")
            logging.error(f"Raw response: {response.text}")
            return f"Error parsing response: {str(e)} - Response was: {response.text}"
    # Fallback to Ollama/OpenAI
    prompt_template = PromptTemplate(
        input_variables=["nl_query", "context"],
        template="""
        Given the context: {context}
        Convert the following natural language query to SQL:
        {nl_query}
        """
    )
    try:
        llm = Ollama(model="llama2")
    except Exception:
        llm = OpenAI()
    return llm(prompt_template.format(nl_query=nl_query, context=context))
