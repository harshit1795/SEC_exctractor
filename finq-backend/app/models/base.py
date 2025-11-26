"""Base model class"""
from sqlalchemy.ext.declarative import declarative_base
from app.database import Base as DBBase

# Use the same Base from database.py
Base = DBBase


