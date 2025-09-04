import os
import json
import logging
from dotenv import load_dotenv
from langchain_community.llms import Ollama, OpenAI
from langchain.prompts import PromptTemplate

# Import Gemini API client
try:
    from google.generativeai import GenerativeModel, configure
except ImportError:
    GenerativeModel = None
    configure = None

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def generate_sql(nl_query: str, context: str) -> str:
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key and GenerativeModel and configure:
        logging.info("Using Gemini API for SQL generation (official library)")
        try:
            configure(api_key=gemini_api_key)
            model = GenerativeModel("gemini-2.0-flash")
            prompt = (
                "You are an expert SQL query generator. Generate SQL queries from natural language. "
                f"Given this context: {context}\n"
                f"Generate SQL for this query: {nl_query}\n"
                "Respond ONLY with a valid JSON object in this format:\n"
                "{\n  \"sql\": \"the SQL query\",\n  \"explanation\": \"brief explanation of what the query does\"\n}"
            )
            response = model.generate_content(prompt)
            logging.debug(f"Gemini response: {response}")
            # Extract the text from Gemini's response
            if hasattr(response, 'text'):
                content = response.text
            elif hasattr(response, 'candidates'):
                content = response.candidates[0].content.parts[0].text
            else:
                content = str(response)
            logging.debug(f"Extracted content: {content}")
            # Parse the JSON from the response text
            try:
                result = json.loads(content)
                logging.info("Successfully parsed JSON response from Gemini")
                return f"SQL: {result['sql']}\nExplanation: {result['explanation']}"
            except Exception as e:
                logging.error(f"Error parsing Gemini response: {str(e)}")
                logging.error(f"Raw response: {content}")
                return f"Error parsing Gemini response: {str(e)} - Response was: {content}"
        except Exception as e:
            logging.error(f"Gemini API error: {str(e)}")
            return f"Gemini API error: {str(e)}"
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
