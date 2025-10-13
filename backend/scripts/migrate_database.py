"""
Database migration script for simplified conversation architecture.
Only conversations table is created - other entities are file-based.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy import text
from src.shared.infrastructure.database.database_config import db_config
from src.conversation.infrastructure.persistence.models import ConversationModel, Base


def run_migration():
    """Run database migration to create conversations table."""
    print("Setting up database...")
    db_config.setup_database()
    
    # Create conversation domain tables
    print("Creating conversation domain tables...")
    Base.metadata.create_all(bind=db_config.engine)
    
    # Verify tables were created
    with db_config.get_session() as session:
        # Detect database type and use appropriate query
        from src.shared.infrastructure.config.environment_config import env_config
        db_type = env_config.get_database_type()
        
        if db_type in ["postgresql", "supabase"]:
            result = session.execute(text("""
                SELECT tablename FROM pg_catalog.pg_tables
                WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'
            """))
        else:
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        
        tables = [row[0] for row in result.fetchall()]
        print(f"Created tables: {tables}")
        
        # Check if our conversations table exists
        expected_table = 'conversations'
        
        if expected_table in tables:
            print(f"✓ Table '{expected_table}' created successfully")
        else:
            print(f"✗ Table '{expected_table}' not found")
    
    print("Migration completed successfully!")
    print("Note: Transcription, Analysis, Persona, and Context are stored as files.")


if __name__ == "__main__":
    run_migration()
