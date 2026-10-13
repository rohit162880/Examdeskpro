"""
Configuration for the Examination Scheduling and Result Processing System.
Supports environment variables with sensible defaults for local development.
"""
import os

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'Rohit@123'),
    'database': os.environ.get('DB_NAME', 'exam_scheduling_db'),
    'autocommit': True,
}

SECRET_KEY = os.environ.get('SECRET_KEY', 'exam_scheduling_secret_key_2024_project24')
