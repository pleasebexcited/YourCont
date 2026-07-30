"""
scripts/init_db.py: Creates the users table in the database

One off setup for the YourCont database.
After Postgres is installed and DATABASE_URL is set in .env, I run this from the terminal.
It loads my local settings, then calls init_schema in app/db.py to create the users table needed for sign up and log in.
Contact tables will be added later with the same approach.
The project root is added to the Python path so "import app" works when I launch the script from the scripts folder.
"""

import os
import sys

from dotenv import load_dotenv

# Without the project root on sys.path, running this from scripts/ cannot see the app package.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

load_dotenv(os.path.join(project_root, ".env"), override=True)

from app.db import init_schema

if __name__ == "__main__":

    # Safe to rerun: init_schema uses IF NOT EXISTS so existing accounts are left alone.
    init_schema()
    print("YourCont users table is ready.")
