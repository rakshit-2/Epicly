from os import environ as env


class Settings:
  DB_PORT = env.get("DB_PORT", 8000)
  DB_NAME = env.get("DB_NAME", "epicly_db")
  DB_HOST = env.get("DB_HOST", "localhost")