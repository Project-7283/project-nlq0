import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

def setup_logger(name: str, log_file: Optional[str] = None, level=logging.INFO):
    """Function to setup as many loggers as you want"""
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger

# Application loggers
app_logger = setup_logger("nlq_app", "logs/app.log")
audit_logger = setup_logger("audit", "logs/audit.log")
performance_logger = setup_logger("performance", "logs/performance.log")

