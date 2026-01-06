"""
Temporary script to fix migration issue on Render.
Run this once to manually add missing columns and update alembic version.
"""
import os
from sqlalchemy import create_engine, text
from config import settings

def fix_migration():
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # Check if columns already exist
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='tasks' 
            AND column_name IN ('status_message', 'error_message')
        """))
        existing_columns = [row[0] for row in result]
        
        # Add missing columns
        if 'status_message' not in existing_columns:
            print("Adding status_message column...")
            conn.execute(text("ALTER TABLE tasks ADD COLUMN status_message TEXT"))
            conn.commit()
            print("✓ Added status_message column")
        else:
            print("✓ status_message column already exists")
            
        if 'error_message' not in existing_columns:
            print("Adding error_message column...")
            conn.execute(text("ALTER TABLE tasks ADD COLUMN error_message TEXT"))
            conn.commit()
            print("✓ Added error_message column")
        else:
            print("✓ error_message column already exists")
        
        # Update alembic version to 002
        print("Updating alembic_version to 002...")
        conn.execute(text("UPDATE alembic_version SET version_num='002'"))
        conn.commit()
        print("✓ Updated alembic_version to 002")
        
    print("\n✅ Migration fix complete!")

if __name__ == "__main__":
    fix_migration()
