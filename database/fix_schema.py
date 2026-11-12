"""
Fix database schema - add default to name column
"""

import sqlite3
import os

def fix_database_schema():
    """Fix the database schema to make name field nullable or add default"""
    
    db_path = 'database/database.db'
    
    if not os.path.exists(db_path):
        print("Database file not found. Please run init_db.py first.")
        return
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check current schema
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("Current users table schema:")
        for col in columns:
            print(f"  {col[1]} - {col[2]} - {'NOT NULL' if col[3] else 'NULL'}")
        
        # Since SQLite doesn't support ALTER COLUMN directly, we need to recreate the table
        print("\nRecreating users table with fixed schema...")
        
        # Create backup table
        cursor.execute("ALTER TABLE users RENAME TO users_old")
        
        # Create new table with correct schema
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(150) NOT NULL DEFAULT '',
                username VARCHAR(80) UNIQUE,
                email VARCHAR(150) UNIQUE NOT NULL,
                password VARCHAR(200) NOT NULL,
                password_hash VARCHAR(200),
                full_name VARCHAR(100),
                age INTEGER,
                gender VARCHAR(10),
                phone VARCHAR(20),
                address VARCHAR(200),
                role VARCHAR(20) DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # Copy data from old table to new table
        cursor.execute("""
            INSERT INTO users (
                id, name, username, email, password, password_hash,
                full_name, age, gender, phone, address, role, is_active, created_at, last_login
            )
            SELECT 
                id, COALESCE(name, full_name, username, ''), 
                username, email, password, password_hash,
                full_name, age, gender, phone, address, role, is_active, created_at, last_login
            FROM users_old
        """)
        
        # Drop old table
        cursor.execute("DROP TABLE users_old")
        
        conn.commit()
        print("✓ Database schema fixed successfully!")
        
    except Exception as e:
        print(f"Error fixing schema: {str(e)}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database_schema()