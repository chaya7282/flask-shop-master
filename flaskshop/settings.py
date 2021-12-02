 # -*- coding: utf-8 -*-
"""Application configuration."""
import os
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
# This is a sample Python script.
import psycopg2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import flask_sqlalchemy
import sqlalchemy.dialects.postgresql
from sqlalchemy.dialects import postgresql

class LocalConfig:
    db_uri = "mysql://root:chaya@localhost:3306/chaya?charset=utf8mb4"

    redis_uri = "redis://localhost:6379"
    esearch_uri = "localhost"
class Config:

    SECRET_KEY = os.getenv("SECRET_KEY", "thisisashop")

    # Redis
    # if redis is enabled, it can be used for:
    #   - cache
    #   - save product description
    #   - save page content
    USE_REDIS = False
    REDIS_URL = os.getenv("REDIS_URI", LocalConfig.redis_uri)

    # Elasticsearch
    # if elasticsearch is enabled, the home page will have a search bar
    # and while add a product, the search index will get update
    USE_ES = False
    ES_HOSTS = [
        os.getenv("ESEARCH_URI", LocalConfig.esearch_uri),
    ]

    # SQLALCHEMY"

    SQLALCHEMY_DATABASE_URI ="mysql://t165ie12h8gw65tx:jty23hwy76q7y275@ao9moanwus0rjiex.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/hxg4ezjfrkkztwyc"
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URI", LocalConfig.db_uri)

    S3_BUCKET = "chayaflaskbacket"
    S3_KEY = "AKIAR3EL7JFQ7PZIAPKJ"
    S3_SECRET = "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"
    AWS_S3_REGION_NAME= "ap-northeast-3"


    SQLALCHEMY_DATABASE_URI= os.getenv('JAWSDB_MARIA_URL')


    JSONIFY_PRETTYPRINT_REGULAR = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_PRE_PING =True
    DATABASE_QUERY_TIMEOUT = 10  # log the slow database query, and unit is second


    SQLALCHEMY_POOL_RECYCLE=3600
    SQLALCHEMY_POOL_TIMEOUT= 20
    # Dir
    APP_DIR = Path(__file__).parent  # This directory
    PROJECT_ROOT = APP_DIR.parent
    STATIC_DIR = APP_DIR / "static"
    UPLOAD_FOLDER = STATIC_DIR /"uploads"
    CATEGORY_IMAGES= STATIC_DIR /"uploads/category"
    UPLOAD_DIR = STATIC_DIR /"uploads"
    DASHBOARD_TEMPLATE_FOLDER = APP_DIR / "templates" / "dashboard"

    BCRYPT_LOG_ROUNDS = 13
    DEBUG_TB_ENABLED = os.getenv("FLASK_DEBUG", False)  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_PROFILER_ENABLED = True
    TEMPLATES_AUTO_RELOAD = True
    MESSAGE_QUOTA = 10

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'esekbekafyad@gmail.com'
    MAIL_PASSWORD = 'chaya7282'