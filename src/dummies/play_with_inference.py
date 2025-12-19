
import os
from dotenv import load_dotenv
from ..services.inference import GeminiService
from pydantic import BaseModel

from enum import Enum

class RoleEnum(Enum):
    Manager = "Manager"
    Employee = "Employee"
    Director = "Director"

load_dotenv()



def main():
    # Initialize GeminiService (requires GEMINI_API_KEY in environment)
    gemini = GeminiService()

    # 1. Structured output: extract info as JSON
    class SalesInfo(BaseModel):
        name: str
        """name of the sales person"""
        role: RoleEnum
        """role of the sales person"""
        department: str
        sales: int
        quarter: str

    content = "John Doe, a sales manager in the Electronics department, achieved $120,000 in sales in Q2."
    try:
        structured = gemini.get_structured_output(content, SalesInfo.model_json_schema())
        print("Structured Output (Pydantic Model):")
        print(structured)
    except Exception as e:
        print("Structured Output Error:", e)
    print("-" * 50)

    # # 2. Summarization
    # long_text = (
    #     "The NLQ Enhancement project enables users to interact with databases using natural language. "
    #     "It leverages vector embeddings for context retrieval and large language models for SQL generation. "
    #     "The system supports multiple LLMs with graceful fallbacks and provides a Streamlit-based UI."
    # )
    # try:
    #     summary = gemini.get_summary(long_text, max_words=30)
    #     print("Summarization:")
    #     print(summary)
    # except Exception as e:
    #     print("Summarization Error:", e)
    # print("-" * 50)

    # # 3. General chat completion
    # chat_message = "What are the benefits of using vector embeddings in NLP?"
    # try:
    #     chat_resp = gemini.chat_completion(chat_message)
    #     print("General Chat Completion:")
    #     print(chat_resp)
    # except Exception as e:
    #     print("Chat Completion Error:", e)
    # print("-" * 50)

    # # 4. Intent analysis
    # user_query = "List all employees who joined after 2020."
    # try:
    #     intent = gemini.analyze_intent(user_query)
    #     print("Intent Analysis:")
    #     print(intent)
    # except Exception as e:
    #     print("Intent Analysis Error:", e)
    # print("-" * 50)

if __name__ == "__main__":
    main()