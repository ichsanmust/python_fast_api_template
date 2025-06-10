from sqlalchemy import MetaData, Table, Column, Integer, String, Text, DateTime
from datetime import datetime
from app.core import config

# schema error log
metadata = MetaData()
error_logs = Table(
    "error_logs", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("message", Text),
    Column("path", String(255)),
    Column("created_date", DateTime, default=datetime.now(config.TIMEZONE)),
)
