import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class FeedbackLog(BaseModel):
    id: str
    timestamp: str
    user_query: str
    generated_sql: str
    rating: int  # 1 for Positive, -1 for Negative
    user_comment: Optional[str] = None
    graph_context: Optional[Dict[str, Any]] = None  # Stores the path/nodes used

class FeedbackService:
    def __init__(self, log_file: str = "feedback_logs.json"):
        self.log_file = log_file
        self._ensure_log_file()

    def _ensure_log_file(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f)

    def log_feedback(self, 
                     user_query: str, 
                     generated_sql: str, 
                     rating: int, 
                     user_comment: str = None,
                     graph_context: Dict[str, Any] = None) -> str:
        
        log_entry = FeedbackLog(
            id=datetime.now().strftime("%Y%m%d%H%M%S%f"),
            timestamp=datetime.now().isoformat(),
            user_query=user_query,
            generated_sql=generated_sql,
            rating=rating,
            user_comment=user_comment,
            graph_context=graph_context
        )

        logs = self._read_logs()
        logs.append(log_entry.dict())
        self._write_logs(logs)
        
        return log_entry.id

    def get_logs(self) -> List[Dict]:
        return self._read_logs()

    def _read_logs(self) -> List[Dict]:
        try:
            with open(self.log_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_logs(self, logs: List[Dict]):
        with open(self.log_file, "w") as f:
            json.dump(logs, f, indent=2)
