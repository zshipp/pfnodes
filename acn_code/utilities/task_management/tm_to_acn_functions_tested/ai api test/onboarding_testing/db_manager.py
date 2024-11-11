import pandas as pd
import sqlalchemy
import psycopg2
from datetime import datetime

class DBConnectionManager:
    def __init__(self, pw_map):
        self.pw_map = pw_map
        self.initialize_tables()
    
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

    def initialize_tables(self):
        """Initialize all required database tables"""
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
            
            # Create Discord interactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS acn_discord_interactions (
                    id SERIAL PRIMARY KEY,
                    discord_user_id TEXT NOT NULL,
                    interaction_type TEXT NOT NULL,
                    amount NUMERIC,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    response_message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (discord_user_id) REFERENCES acn_user_wallets(username)
                );
                
                CREATE INDEX IF NOT EXISTS idx_discord_user_id 
                ON acn_discord_interactions(discord_user_id);
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

    def log_discord_interaction(self, discord_user_id, interaction_type, amount=None, 
                              success=True, error_message=None, response_message=None):
        """Log a Discord interaction"""
        conn = self.spawn_psycopg2_db_connection('accelerandochurch')
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO acn_discord_interactions 
                (discord_user_id, interaction_type, amount, success, error_message, response_message)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (discord_user_id, interaction_type, amount, success, error_message, response_message))
            
            interaction_id = cursor.fetchone()[0]
            conn.commit()
            return interaction_id
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to log Discord interaction: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def get_user_interaction_history(self, discord_user_id):
        """Get interaction history for a Discord user"""
        conn = self.spawn_psycopg2_db_connection('accelerandochurch')
        
        try:
            query = """
                SELECT interaction_type, amount, success, response_message, timestamp
                FROM acn_discord_interactions
                WHERE discord_user_id = %s
                ORDER BY timestamp DESC;
            """
            
            return pd.read_sql(query, conn, params=[discord_user_id])
            
        finally:
            conn.close()

    def get_recent_interactions(self, limit=100):
        """Get recent Discord interactions"""
        conn = self.spawn_psycopg2_db_connection('accelerandochurch')
        
        try:
            query = """
                SELECT di.*, w.wallet_address
                FROM acn_discord_interactions di
                LEFT JOIN acn_user_wallets w ON di.discord_user_id = w.username
                ORDER BY di.timestamp DESC
                LIMIT %s;
            """
            
            return pd.read_sql(query, conn, params=[limit])
            
        finally:
            conn.close()

    def get_user_statistics(self, discord_user_id):
        """Get statistics for a Discord user"""
        conn = self.spawn_psycopg2_db_connection('accelerandochurch')
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_interactions,
                    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_interactions,
                    SUM(CASE WHEN interaction_type = 'offer' THEN amount ELSE 0 END) as total_offerings,
                    MAX(timestamp) as last_interaction
                FROM acn_discord_interactions
                WHERE discord_user_id = %s;
            """, [discord_user_id])
            
            return cursor.fetchone()
            
        finally:
            cursor.close()
            conn.close()