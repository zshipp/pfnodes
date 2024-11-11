import pandas as pd
import sqlalchemy
import psycopg2

class DBConnectionManager:
    def __init__(self, pw_map):
        self.pw_map = pw_map
        self.initialize_wallet_table()
    
    def spawn_sqlalchemy_db_connection_for_user(self, user_name):
        """Get database connection using connection string from pw_map"""
        db_connstring = self.pw_map[f'{user_name}__postgresconnstring']
        return sqlalchemy.create_engine(db_connstring)
    
    def spawn_psycopg2_db_connection(self, user_name):
        """Create psycopg2 connection from connection string"""
        db_connstring = self.pw_map[f'{user_name}__postgresconnstring']
        db_user = db_connstring.split('://')[1].split(':')[0]
        db_password = db_connstring.split('://')[1].split(':')[1].split('@')[0]
        db_host = db_connstring.split('://')[1].split(':')[1].split('@')[1].split('/')[0]
        db_name = db_connstring.split('/')[-1:][0]
        
        return psycopg2.connect(
            user=db_user, 
            password=db_password, 
            host=db_host, 
            database=db_name
        )

    def initialize_wallet_table(self):
        """Initialize wallet storage table"""
        conn = self.spawn_psycopg2_db_connection('accelerandochurch')
        cursor = conn.cursor()
        
        try:
            # Create wallet table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS acn_user_wallets (
                    username VARCHAR(255) PRIMARY KEY,
                    wallet_address VARCHAR(255) UNIQUE NOT NULL,
                    wallet_seed TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create access timestamp update trigger
            cursor.execute("""
                CREATE OR REPLACE FUNCTION update_last_accessed()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.last_accessed = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql';

                DROP TRIGGER IF EXISTS update_wallet_last_accessed ON acn_user_wallets;
                CREATE TRIGGER update_wallet_last_accessed
                    BEFORE UPDATE ON acn_user_wallets
                    FOR EACH ROW
                    EXECUTE FUNCTION update_last_accessed();
            """)
            
            conn.commit()
        finally:
            cursor.close()
            conn.close()