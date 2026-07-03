-- Runs automatically the first time the Postgres data volume is initialized
-- (files in /docker-entrypoint-initdb.d are executed on a fresh volume only).
--
-- Enables the pgvector extension required by mem0ai long-term memory. Application
-- tables (user, session, thread) and the LangGraph checkpoint tables are created
-- at app startup by SQLModel and the AsyncPostgresSaver, so they are not defined here.

CREATE EXTENSION IF NOT EXISTS vector;
