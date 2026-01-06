import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import os

def setup_database():
    load_dotenv()
    
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5433")
    db_name = os.getenv("DB_NAME", "weather_db")
    
    print(f"Attempting to connect to PostgreSQL:")
    print(f"  Host: {db_host}")
    print(f"  Port: {db_port}")
    print(f"  User: {db_user}")
    
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"✓ Database '{db_name}' already exists")
        else:
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(db_name)
                )
            )
            print(f"✓ Database '{db_name}' created successfully")
        
        cursor.close()
        conn.close()
        
        test_conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        test_conn.close()
        print(f"Successfully connected to '{db_name}' database")
        print("Database setup complete! You can now run your notebook.")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"Connection Error:")
        print(f"  {str(e)}")
        print(f"Please check:")
        print(f"PostgreSQL is running on port {db_port}")
        print(f"Username '{db_user}' is correct")
        print(f"Password in .env file is correct")
        print(f"PostgreSQL is accepting connections on {db_host}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        return False

if __name__ == "__main__":
    setup_database()
