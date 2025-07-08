#!/usr/bin/env python
"""
Script to initialize the database with initial keywords and talking points.
This script connects directly to the database using the correct Docker service name.
"""
import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.keyword import Keyword, TalkingPoint, Base
from app.schemas.keyword import KeywordCreate, TalkingPointCreate
from app.crud import keyword as keyword_crud

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection settings for Docker environment
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "db")  # Use 'db' as the service name in Docker Compose
POSTGRES_DB = os.getenv("POSTGRES_DB", "aiaudio")
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initial keywords data with talking points
INITIAL_KEYWORDS = [
    {
        "text": "pricing",
        "description": "Discussion about product pricing",
        "threshold": 0.7,
        "talking_points": [
            {
                "title": "Pricing Structure",
                "content": "Our pricing is based on a tiered model with discounts for annual commitments.",
                "priority": 1
            },
            {
                "title": "ROI Calculator",
                "content": "We can provide an ROI calculator to demonstrate the value of our solution for your specific use case.",
                "priority": 2
            }
        ]
    },
    {
        "text": "competitor",
        "description": "Mentions of competitor products",
        "threshold": 0.8,
        "talking_points": [
            {
                "title": "Competitive Advantages",
                "content": "Our solution offers superior accuracy and real-time capabilities compared to competitors.",
                "priority": 1
            },
            {
                "title": "Migration Path",
                "content": "We offer a seamless migration path from competitor products with dedicated support.",
                "priority": 2
            }
        ]
    },
    {
        "text": "integration",
        "description": "Questions about integrating with other systems",
        "threshold": 0.7,
        "talking_points": [
            {
                "title": "API Documentation",
                "content": "We provide comprehensive API documentation and SDKs for all major programming languages.",
                "priority": 1
            },
            {
                "title": "Pre-built Integrations",
                "content": "We have pre-built integrations with popular CRM and sales enablement tools.",
                "priority": 2
            }
        ]
    },
    {
        "text": "security",
        "description": "Questions about data security and compliance",
        "threshold": 0.8,
        "talking_points": [
            {
                "title": "Data Encryption",
                "content": "All data is encrypted both in transit and at rest using industry-standard encryption protocols.",
                "priority": 1
            },
            {
                "title": "Compliance Certifications",
                "content": "We are SOC 2 Type II certified and GDPR compliant. We can provide our security documentation upon request.",
                "priority": 2
            }
        ]
    },
    {
        "text": "support",
        "description": "Questions about customer support",
        "threshold": 0.7,
        "talking_points": [
            {
                "title": "Support Tiers",
                "content": "We offer 24/7 support for enterprise customers and business-hours support for standard plans.",
                "priority": 1
            },
            {
                "title": "Implementation Support",
                "content": "All customers receive dedicated implementation support during the onboarding process.",
                "priority": 2
            }
        ]
    }
]


def init_db():
    """
    Initialize the database with initial data.
    """
    db = SessionLocal()
    try:
        # Create keywords
        for keyword_data in INITIAL_KEYWORDS:
            # Check if keyword already exists
            existing_keyword = keyword_crud.get_keyword_by_text(db, keyword_data["text"])
            if existing_keyword:
                logger.info(f"Keyword '{keyword_data['text']}' already exists, skipping.")
                continue
            
            # Create keyword
            keyword_create = KeywordCreate(
                text=keyword_data["text"],
                description=keyword_data["description"],
                threshold=keyword_data["threshold"]
            )
            db_keyword = keyword_crud.create_keyword(db, keyword_create)
            logger.info(f"Created keyword: {db_keyword.text}")
            
            # Create talking points for this keyword
            for tp_data in keyword_data["talking_points"]:
                talking_point_create = TalkingPointCreate(
                    title=tp_data["title"],
                    content=tp_data["content"],
                    priority=tp_data["priority"]
                )
                db_talking_point = keyword_crud.create_talking_point(
                    db, db_keyword.id, talking_point_create
                )
                logger.info(f"Created talking point: {db_talking_point.title}")
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Creating initial keywords and talking points")
    init_db()
    logger.info("Initial data created successfully")
