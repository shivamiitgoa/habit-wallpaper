import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get environment (default to 'prod')
ENV = os.getenv('ENV', 'prod')

# Database configurations
DB_NAME = 'habits_test.db' if ENV == 'test' else 'habits.db'

# Flag to determine if tables should be reset
RESET_TABLES = ENV == 'test' 