#!/usr/bin/env python
"""
Script to initialize the database with initial data.
Run this script to populate the database with initial keywords and talking points.
"""
import os
import sys
import logging

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.init_data import main

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
    print("Database initialized with initial keywords and talking points.")
