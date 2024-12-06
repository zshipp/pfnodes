import pandas as pd
import sqlalchemy
import psycopg2
from datetime import datetime
from kms_encryption import encrypt_data, decrypt_data

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
                    reason TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (discord_user_id) REFERENCES acn_user_wallets(username)
                );
                
                CREATE INDEX IF NOT EXISTS idx_discord_user_id 
                ON acn_discord_interactions(discord_user_id);
            """)
         
            # Create user reputation table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS acn_user_reputation (
                    user_id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    reputation_points INT DEFAULT 0,
                    rank VARCHAR(50) DEFAULT 'Akromeni',
                    last_activity TIMESTAMP DEFAULT NULL
                );
            """)

            # Create user reasons table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS acn_user_reasons (
                    username VARCHAR(255) PRIMARY KEY,
                    reason TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS acn_blockchain_transactions (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255),
                    interaction_id INTEGER,
                    tx_hash VARCHAR(255),
                    tx_type VARCHAR(50),  -- 'offering', 'tithe', etc
                    amount NUMERIC,
                    status VARCHAR(50),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES acn_user_wallets(username),
                    FOREIGN KEY (interaction_id) REFERENCES acn_discord_interactions(id)
                );
        
                CREATE INDEX IF NOT EXISTS idx_blockchain_tx_user 
                ON acn_blockchain_transactions(username);
        
                CREATE INDEX IF NOT EXISTS idx_blockchain_tx_hash 
                ON acn_blockchain_transactions(tx_hash);
            """)

            # PFT foundation node transaction scraping data:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS xrpl_raw_transactions (
                    id SERIAL PRIMARY KEY,
                    tx_hash TEXT UNIQUE,
                    ledger_index INTEGER,
                    date TIMESTAMPTZ,
                    from_address TEXT,
                    to_address TEXT,
                    amount NUMERIC,
                    currency TEXT,
                    fee NUMERIC,
                    memo_type TEXT,
                    memo_format TEXT,
                    memo_data TEXT,
                    tx_json JSONB,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );

                CREATE INDEX IF NOT EXISTS idx_xrpl_tx_hash 
                ON xrpl_raw_transactions(tx_hash);
    
                CREATE INDEX IF NOT EXISTS idx_xrpl_addresses 
                ON xrpl_raw_transactions(from_address, to_address);
            """)

            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def log_discord_interaction(self, discord_user_id, interaction_type, amount=None, 
                              success=True, error_message=None, response_message=None, reason=None):
        """Log a Discord interaction"""
        conn = self.spawn_psycopg2_db_connection('accelerandochurch')
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO acn_discord_interactions 
                (discord_user_id, interaction_type, amount, success, error_message, response_message, reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (discord_user_id, interaction_type, amount, success, error_message, response_message, reason))
            
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

    def log_initiation_waiting_period(self, username, initiation_ready_date):
        """Log the initiation waiting period in acn_initiation_periods table."""
        conn = self.spawn_psycopg2_db_connection('accelerandochurch')
        cursor = conn.cursor()
    
        try:
            cursor.execute("""
                INSERT INTO acn_initiation_periods (username, initiation_ready_date)
                VALUES (%s, %s)
                ON CONFLICT (username) DO UPDATE 
                SET initiation_ready_date = EXCLUDED.initiation_ready_date;
            """, (username, initiation_ready_date))
        
            conn.commit()
            print(f"Initiation waiting period logged for user {username}")
        
        except Exception as e:
            conn.rollback()
            print(f"Error logging initiation waiting period for user {username}: {str(e)}")
        
        finally:
            cursor.close()
            conn.close()

    def get_initiation_waiting_period(self, username):
        """Retrieves the initiation waiting period data for a user."""
        conn = self.spawn_psycopg2_db_connection('accelerandochurch')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT initiation_ready_date
                FROM acn_initiation_periods
                WHERE username = %s;
            """, (username,))
            result = cursor.fetchone()
            if result:
                return {"initiation_ready_date": result[0]}
            return None
        except Exception as e:
            raise Exception(f"Failed to retrieve initiation waiting period: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def is_user_locked_out(self, username):
        """Check if the user is locked out due to an active initiation waiting period."""
        try:
            conn = self.spawn_psycopg2_db_connection('accelerandochurch')
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT initiation_ready_date
                    FROM acn_initiation_periods
                    WHERE username = %s AND initiation_ready_date > CURRENT_TIMESTAMP;
                """, (username,))
                result = cursor.fetchone()
                return result is not None
            finally:
                cursor.close()
                conn.close()
        except Exception as e:
            raise Exception(f"Failed to check user lockout status: {str(e)}")

    def update_reputation(self, username, points_earned):
        """
        Updates the reputation points of a user without altering their rank.
        Rank updates are handled separately in the update_rank function.

        :param username: The username of the user.
        :param points_earned: The reputation points to add.
        """
        try:
            conn = self.spawn_psycopg2_db_connection('accelerandochurch')
            cursor = conn.cursor()
    
            # Fetch current reputation points
            cursor.execute("""
                SELECT reputation_points FROM acn_user_reputation WHERE username = %s;
            """, (username,))
            result = cursor.fetchone()
    
            if not result:
                # If the user doesn't exist in the reputation table, initialize their entry with NULL rank
                cursor.execute("""
                    INSERT INTO acn_user_reputation (username, reputation_points, rank)
                    VALUES (%s, %s, NULL);
                """, (username, points_earned))
                conn.commit()
                print(f"Initialized reputation for {username} with {points_earned} points.")
            else:
                # Update reputation points
                current_points = result[0]
                new_points = current_points + points_earned
        
                cursor.execute("""
                    UPDATE acn_user_reputation
                    SET reputation_points = %s, last_activity = NOW()
                    WHERE username = %s;
                """, (new_points, username))
                conn.commit()
                print(f"Updated reputation for {username}: {new_points} points.")

        except Exception as e:
            print(f"Failed to update reputation for {username}: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def log_activity(self, username: str, activity_type: str, timestamp: datetime = None):
        """
        Logs user activity in the reputation table.

        :param username: The username of the user
        :param activity_type: The type of activity to log (e.g., 'status_check', 'offering', 'tithe')
        :param timestamp: Optional timestamp; defaults to the current time
        """
        try:
            if not timestamp:
                timestamp = datetime.now()

            conn = self.spawn_psycopg2_db_connection('accelerandochurch')
            cursor = conn.cursor()

            # Update last_activity and optionally add reputation points
            cursor.execute("""
                INSERT INTO acn_user_reputation (username, last_activity)
                VALUES (%s, %s)
                ON CONFLICT (username) DO UPDATE 
                SET last_activity = EXCLUDED.last_activity
            """, (username, timestamp))

            conn.commit()
            print(f"Logged activity for {username}: {activity_type} at {timestamp}")
        except Exception as e:
            print(f"Error logging activity for {username}: {str(e)}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def update_rank(self, username, initiation_ceremony_completed=False):
        """Updates the rank of a user based on their progression through onboarding steps."""
        try:
            conn = self.spawn_psycopg2_db_connection('accelerandochurch')
            cursor = conn.cursor()

            # Get current rank
            cursor.execute("""
                SELECT rank FROM acn_user_reputation WHERE username = %s;
            """, (username,))
            result = cursor.fetchone()

            if not result:
                # New user - insert with Akromeni rank
                cursor.execute("""
                    INSERT INTO acn_user_reputation (username, rank)
                    VALUES (%s, 'Akromeni');
                """, (username,))
                current_rank = 'Akromeni'
            else:
                current_rank = result[0]

            # Check for rank progression conditions
            if current_rank == 'Akromeni':
                # Check if they've completed submit_offering
                cursor.execute("""
                    SELECT COUNT(*) FROM acn_discord_interactions
                    WHERE discord_user_id = %s 
                    AND interaction_type = 'submit_offering'
                    AND success = true;
                """, (username,))
                has_submitted_offering = cursor.fetchone()[0] > 0

                if has_submitted_offering:
                    new_rank = 'Mystai'
                    cursor.execute("""
                        UPDATE acn_user_reputation
                        SET rank = %s, last_activity = NOW()
                        WHERE username = %s;
                    """, (new_rank, username))

            elif current_rank == 'Mystai' and initiation_ceremony_completed:
                # Only progress to Acolyte if ceremony is completed
                new_rank = 'Acolyte'
                cursor.execute("""
                    UPDATE acn_user_reputation
                    SET rank = %s, last_activity = NOW()
                    WHERE username = %s;
                """, (new_rank, username))

            conn.commit()

        except Exception as e:
            print(f"Error updating rank for {username}: {e}")
            if conn:
                conn.rollback()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def save_user_reason(self, username, reason):
        conn = self.spawn_psycopg2_db_connection('accelerandochurch')
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO acn_user_reasons (username, reason)
                VALUES (%s, %s)
                ON CONFLICT (username) DO UPDATE SET reason = EXCLUDED.reason;
            """, (username, reason))
            conn.commit()
        except Exception as e:
            print(f"Error saving user reason: {e}")
        finally:
            cursor.close()
            conn.close()

    def log_blockchain_transaction(self, username, interaction_id, tx_hash, tx_type, amount, status='completed'):
        """Log a blockchain transaction."""
        conn = self.spawn_psycopg2_db_connection('accelerandochurch')
        cursor = conn.cursor()
    
        try:
            cursor.execute("""
                INSERT INTO acn_blockchain_transactions 
                (username, interaction_id, tx_hash, tx_type, amount, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (username, interaction_id, tx_hash, tx_type, amount, status))
        
            tx_id = cursor.fetchone()[0]
            conn.commit()
            return tx_id
        
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to log blockchain transaction: {str(e)}")
        finally:
            cursor.close()
            conn.close()
    def get_user_blockchain_transactions(self, username):
        """Get all blockchain transactions for a user."""
        conn = self.spawn_psycopg2_db_connection('accelerandochurch')
        cursor = conn.cursor()
    
        try:
            cursor.execute("""
                SELECT bt.*, di.interaction_type, di.reason
                FROM acn_blockchain_transactions bt
                LEFT JOIN acn_discord_interactions di ON bt.interaction_id = di.id
                WHERE bt.username = %s
                ORDER BY bt.timestamp DESC;
            """, (username,))
        
            return cursor.fetchall()
        
        finally:
            cursor.close()
            conn.close()

    def ensure_user_exists(self, username):
        """Ensures user exists in reputation table with initial rank."""
        conn = self.spawn_psycopg2_db_connection('accelerandochurch')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO acn_user_reputation (username, rank)
                VALUES (%s, 'Akromeni')
                ON CONFLICT (username) DO NOTHING;
            """, (username,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def save_wallet_seed(user_id, wallet_seed):
        # Encrypt the wallet seed before saving
        encrypted_seed = encrypt_data(wallet_seed)
        db.save('wallet_seeds', user_id, encrypted_seed)

    def get_wallet_seed(user_id):
        # Retrieve and decrypt the wallet seed
        encrypted_seed = db.get('wallet_seeds', user_id)
        if encrypted_seed:
            return decrypt_data(encrypted_seed)
        return None
