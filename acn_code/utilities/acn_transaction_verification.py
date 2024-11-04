import datetime
import psycopg2
import re
from password_map_loader import PasswordMapLoader  # Import PasswordMapLoader

# Connect to PostgreSQL database
def connect_to_db():
    password_loader = PasswordMapLoader()
    db_user = password_loader.get_password("POSTGRES_USER")
    db_password = password_loader.get_password("POSTGRES_PASSWORD")

    try:
        connection = psycopg2.connect(
            database="acn_database",
            user=db_user,
            password=db_password,
            host="localhost",
            port="5432"
        )
        print("Connection to database successful.")
        return connection
    except Exception as e:
        print("Error connecting to database:", e)
        return None

class ACNTransactionHandler:
    def __init__(self, db_connection, member_table='Members', submission_table='Submissions'):
        self.db_connection = db_connection
        self.member_table = member_table
        self.submission_table = submission_table
    
    def log_and_verify_submission(self, transaction_data):
        """
        Logs and verifies a submission to the Submissions table.
        
        Parameters:
        transaction_data (dict): Contains transaction details such as 'member_id', 
                                 'wallet_address', 'amount', 'timestamp', 'memo_data', etc.
        
        Returns:
        dict: Verification result with 'status' and 'reason' for any unverified submissions.
        """
        # Extract transaction data
        member_id = transaction_data.get("member_id")
        wallet_address = transaction_data.get("wallet_address")
        amount = transaction_data.get("amount")
        timestamp = transaction_data.get("timestamp", datetime.datetime.now())
        memo_data = transaction_data.get("memo_data")
        
        # Step 1: Log transaction in the Submissions table
        self._log_submission(member_id, wallet_address, amount, timestamp, memo_data)
        
        # Step 2: Cross-verify member ID and wallet address
        if not self._verify_member_wallet(member_id, wallet_address):
            return {"status": "unverified", "reason": "Wallet address does not match member ID"}
        
        # Step 3: Additional verification criteria (e.g., tithe minimums, timestamp validity)
        verification_result = self._verify_submission_criteria(member_id, amount, memo_data)

        if "COLLABORATION_RITUAL" in memo_data:
        logging.info(f"Collaboration ritual detected: {memo_data}")
        
        # Update verification status in the database
        self._update_verification_status(verification_result, member_id, timestamp)
        
        return verification_result
    
    def _log_submission(self, member_id, wallet_address, amount, timestamp, memo_data):
        """
        Logs the submission data in the Submissions table.
        """
        with self.db_connection.connect() as conn:
            conn.execute(f"""
                INSERT INTO {self.submission_table} (member_id, wallet_address, amount, timestamp, memo_data)
                VALUES (:member_id, :wallet_address, :amount, :timestamp, :memo_data)
            """, {
                "member_id": member_id,
                "wallet_address": wallet_address,
                "amount": amount,
                "timestamp": timestamp,
                "memo_data": memo_data
            })
    
    def _verify_member_wallet(self, member_id, wallet_address):
        """
        Verifies that the wallet address matches the registered member_id.
        """
        with self.db_connection.connect() as conn:
            result = conn.execute(f"""
                SELECT wallet_address FROM {self.member_table} WHERE member_id = :member_id
            """, {"member_id": member_id}).fetchone()
        
        if result and result["wallet_address"] == wallet_address:
            return True
        return False
    
    def _verify_submission_criteria(self, member_id, amount, memo_data):
        """
        Verifies additional criteria based on memo_data content and transaction amount.
        
        Returns:
        dict: Verification result containing 'status' and optional 'reason'.
        """
        # Example criteria: minimum amount for tithe
        if "TITHE_SUBMISSION" in memo_data and amount < 10:  # Minimum tithe set at 10 units
            return {"status": "unverified", "reason": "Tithe amount below minimum"}
        
        # Check for ritual submissions
        if "RITUAL_SUBMISSION" in memo_data:
            ritual_id = self._extract_ritual_id(memo_data)
        if not self._is_valid_ritual(ritual_id, member_id):
            return {"status": "unverified", "reason": "Invalid ritual submission"}

        # Collaboration rituals with specific types
        if "COLLABORATION_RITUAL:TYPE1" in memo_data:
            return {"status": "verified", "reason": "Collaboration ritual Type 1 verified"}
        elif "COLLABORATION_RITUAL:TYPE2" in memo_data:
            return {"status": "verified", "reason": "Collaboration ritual Type 2 verified"}
        elif "COLLABORATION_RITUAL" in memo_data:
            return {"status": "verified", "reason": "General collaboration ritual verified"}

    return {"status": "verified"}
    
    def _extract_ritual_id(self, memo_data):
        """
        Extracts ritual_id from memo_data if present.
        """
        # Assuming ritual_id follows "RITUAL_SUBMISSION:RID123"
        match = re.search(r'RITUAL_SUBMISSION:(RID\d+)', memo_data)
        return match.group(1) if match else None
    
    def _is_valid_ritual(self, ritual_id, member_id):
        """
        Checks if a ritual_id is valid for the member_id.
        """
        # Example placeholder logic; implement actual database check
        valid_rituals = ["RID001", "RID002"]  # Example valid rituals
        return ritual_id in valid_rituals
    
    def _update_verification_status(self, verification_result, member_id, timestamp):
        """
        Updates the verification status in the Submissions table.
        """
        with self.db_connection.connect() as conn:
            conn.execute(f"""
                UPDATE {self.submission_table}
                SET verification_status = :status, verification_reason = :reason
                WHERE member_id = :member_id AND timestamp = :timestamp
            """, {
                "status": verification_result["status"],
                "reason": verification_result.get("reason", ""),
                "member_id": member_id,
                "timestamp": timestamp
            })

if __name__ == "__main__":
    db_connection = connect_to_db()
    if db_connection:
        db_connection.close()  # Close the connection after testing
