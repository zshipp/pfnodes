"""
ACN Task Management
This file handles the task management system for the Accelerando Church Node (ACN).
It includes functions for proposing tasks, tracking task status, verifying completion, and logging.
"""

import datetime
import re
from password_map_loader import PasswordMapLoader
from ACN_Utilities import ACNUtilities
import psycopg2

# Database connection function
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


class ACNTaskManagement:
    def __init__(self, pw_map):
        """
        Initialize the ACN Task Management, set up tools, and define default configurations.
        
        Arguments:
        - pw_map: Password map dictionary for secure access to necessary resources.
        """
        self.pw_map = pw_map
        self.utilities = ACNUtilities(pw_map=pw_map)
        self.db_connection = connect_to_db()
        self.default_task_model = 'chatgpt-4o-latest'

    def propose_task(self, task_description, task_type="PROPOSED PF"):
        """
        Creates a new task proposal with relevant details.

        Arguments:
        - task_description: Description of the proposed task.
        - task_type: Type of task, defaulting to "PROPOSED PF" for ACN-specific proposals.

        Returns:
        - Confirmation message and task ID.
        """
        task_id = self.utilities.generate_custom_id()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        memo_data = f"{task_type} {task_description} .. {task_id}"
        
        # Log task proposal with details
        log_entry = {
            "task_id": task_id,
            "description": task_description,
            "type": task_type,
            "timestamp": timestamp,
            "status": "proposed"
        }
        # Here, save `log_entry` to database or file as needed (assuming a database connection in `utilities`)

        return f"Task proposed successfully with ID {task_id}."

    def log_task_status(self, task_id, new_status):
        """
        Updates the status of an existing task in the system.

        Arguments:
        - task_id: ID of the task to update.
        - new_status: New status for the task (e.g., 'completed', 'in-progress', 'verified').

        Returns:
        - Confirmation message with task ID and new status.
        """
        # Retrieve task, update status, and log update
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = {
            "task_id": task_id,
            "status": new_status,
            "timestamp": timestamp
        }
        # Log the `log_entry` with the updated status in database or file

        return f"Task {task_id} updated to status '{new_status}'."

    def log_and_verify_submission(self, transaction_data):
    """
    Logs and verifies a submission, handling both individual and group submissions.
    
    Parameters:
    - transaction_data (dict): Contains 'member_ids', 'wallet_address', 'amount', 'timestamp', 
                               'memo_data', etc.
    
    Returns:
    - dict: Verification result with 'status' and 'reason' for any unverified submissions.
    """
    # Extract member IDs for group transactions or a single ID for individual
    member_ids = transaction_data.get("member_ids", [transaction_data.get("member_id")])
    wallet_address = transaction_data.get("wallet_address")
    amount = transaction_data.get("amount")
    timestamp = transaction_data.get("timestamp")
    memo_data = transaction_data.get("memo_data")
    transaction_type = self._classify_transaction(memo_data)

    # Conditional handling for group rituals
    if transaction_type == "collaboration_ritual" and member_ids:
        for member_id in member_ids:
            # Log each member's participation in the Submissions table
            self._log_submission(member_id, wallet_address, amount, timestamp, memo_data, transaction_type)
        
        # Log the group participation to GroupParticipation table
        self._log_group_participation(member_ids, transaction_data.get("ritual_id"), timestamp)

        return {"status": "verified", "reason": "Group ritual logged successfully"}

    else:
        # Log non-group transactions as usual
        member_id = member_ids[0] if isinstance(member_ids, list) else transaction_data.get("member_id")
        self._log_submission(member_id, wallet_address, amount, timestamp, memo_data, transaction_type)

        # Verification based on transaction type
        verification_result = self._verify_transaction(transaction_type, transaction_data)

        # Update verification status in Submissions table
        self._update_verification_status(verification_result, member_id, timestamp)
        
        return verification_result

def log_and_verify_submission(self, transaction_data):
    """
    Logs and verifies a submission, handling both individual and group submissions.
    
    Parameters:
    - transaction_data (dict): Contains 'member_ids', 'wallet_address', 'amount', 'timestamp', 
                               'memo_data', etc.
    
    Returns:
    - dict: Verification result with 'status' and 'reason' for any unverified submissions.
    """
    # Extract member IDs for group transactions or a single ID for individual
    member_ids = transaction_data.get("member_ids", [transaction_data.get("member_id")])
    wallet_address = transaction_data.get("wallet_address")
    amount = transaction_data.get("amount")
    timestamp = transaction_data.get("timestamp")
    memo_data = transaction_data.get("memo_data")
    transaction_type = self._classify_transaction(memo_data)

    # Conditional handling for group rituals
    if transaction_type == "collaboration_ritual" and member_ids:
        for member_id in member_ids:
            # Log each member's participation in the Submissions table
            self._log_submission(member_id, wallet_address, amount, timestamp, memo_data, transaction_type)
        
        # Log the group participation to GroupParticipation table
        self._log_group_participation(member_ids, transaction_data.get("ritual_id"), timestamp)

        return {"status": "verified", "reason": "Group ritual logged successfully"}

    else:
        # Log non-group transactions as usual
        member_id = member_ids[0] if isinstance(member_ids, list) else transaction_data.get("member_id")
        self._log_submission(member_id, wallet_address, amount, timestamp, memo_data, transaction_type)

        # Verification based on transaction type
        verification_result = self._verify_transaction(transaction_type, transaction_data)

        # Update verification status in Submissions table
        self._update_verification_status(verification_result, member_id, timestamp)
        
        return verification_result





        # Step 2: Verify based on transaction type ------------------------------------------------------------
        if transaction_type == "financial":
            verification_result = self.verify_financial_transaction(transaction_data)
        elif transaction_type == "ritual":
            verification_result = self.verify_ritual_activity(transaction_data)
        elif transaction_type == "collaboration_ritual":
            verification_result = self._verify_collaboration_ritual(transaction_data)
        else:
            verification_result = {"status": "unverified", "reason": "Unknown transaction type"}

        # Update verification status in the database for each member
        for member_id in member_ids:
            self._update_verification_status(
                verification_result,
                member_id=member_id,
                timestamp=transaction_data.get("timestamp")
            )
        return verification_result

    def verify_financial_transaction(self, transaction_data):
        """
        Verifies a financial transaction, ensuring tithe minimums and other criteria are met.
        
        Parameters:
        - transaction_data (dict): Contains 'member_id', 'wallet_address', 'amount', 'memo_data', etc.
        
        Returns:
        - dict: Verification result.
        """
        """
        Routes verification to the appropriate method based on transaction type.
        """
        if transaction_type == "financial":
            return self.verify_financial_transaction(transaction_data)
        elif transaction_type == "ritual":
            return self.verify_ritual_activity(transaction_data)
        elif transaction_type == "collaboration_ritual":
            return self._verify_collaboration_ritual(transaction_data)
        else:
            return {"status": "unverified", "reason": "Unknown transaction type"}
        amount = transaction_data.get("amount")
        if amount < 10:  # Example minimum amount
            return {"status": "unverified", "reason": "Tithe amount below minimum"}
        
        return {"status": "verified"}

    def verify_ritual_activity(self, transaction_data):
        """
        Verifies a ritual activity submission.
        
        Parameters:
        - transaction_data (dict): Contains 'member_id', 'memo_data', etc.
        
        Returns:
        - dict: Verification result.
        """
        memo_data = transaction_data.get("memo_data")
        ritual_id = self._extract_ritual_id(memo_data)
        member_id = transaction_data.get("member_id")

        if not self._is_valid_ritual(ritual_id, member_id):
            return {"status": "unverified", "reason": "Invalid ritual submission"}
        
        return {"status": "verified"}

    def _verify_collaboration_ritual(self, transaction_data):
        """
        Verifies a collaboration ritual transaction.
        
        Parameters:
        - transaction_data (dict): Contains 'member_id', 'memo_data', etc.
        
        Returns:
        - dict: Verification result with 'status' and optional 'reason'.
        """
        memo_data = transaction_data.get("memo_data")
        participant_id = transaction_data.get("member_id")

        if "COLLABORATION_RITUAL" not in memo_data:
            return {"status": "unverified", "reason": "Invalid collaboration ritual memo format"}

        participant_count = transaction_data.get("participant_count", 1)
        if participant_count < 2:
            return {"status": "unverified", "reason": "Collaboration ritual requires more participants"}

        return {"status": "verified"}

    def _log_group_participation(self, member_ids, transaction_data):
        """
        Logs participation for group rituals in a separate GroupParticipation table.
        
        Parameters:
        - member_ids (list): List of participant IDs involved in the ritual.
        - transaction_data (dict): Contains transaction details.
        """
        timestamp = transaction_data.get("timestamp")
        ritual_id = self._extract_ritual_id(transaction_data.get("memo_data"))

        with self.db_connection.cursor() as cursor:
            for member_id in member_ids:
                cursor.execute("""
                    INSERT INTO GroupParticipation (ritual_id, member_id, timestamp)
                    VALUES (%s, %s, %s)
                """, (ritual_id, member_id, timestamp))
            self.db_connection.commit()

    def _log_submission(self, member_id, wallet_address, amount, timestamp, memo_data, transaction_type):
        """
        Logs the submission data in the Submissions table.
        """
        with self.db_connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO Submissions (member_id, wallet_address, amount, timestamp, memo_data, transaction_type)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (member_id, wallet_address, amount, timestamp, memo_data, transaction_type))
            self.db_connection.commit()

    def _verify_member_wallet(self, member_id, wallet_address):
        """
        Verifies that the wallet address matches the registered member_id.
        """
        with self.db_connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT wallet_address FROM Members WHERE member_id = %s
            """, (member_id,))
            result = cursor.fetchone()
        
        return result and result[0] == wallet_address

    def _update_verification_status(self, verification_result, member_id, timestamp):
        """
        Updates the verification status in the Submissions table.
        """
        with self.db_connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE Submissions
                SET verification_status = %s, verification_reason = %s
                WHERE member_id = %s AND timestamp = %s
            """, (verification_result["status"], verification_result.get("reason", ""), member_id, timestamp))
            self.db_connection.commit()

    def _classify_transaction(self, memo_data):
        """
        Classifies the transaction based on memo data. Returns 'financial', 'ritual', 'collaboration_ritual', or 'unknown'.
        """
        if "TITHE_SUBMISSION" in memo_data or "DONATION" in memo_data:
            return "financial"
        elif "RITUAL_SUBMISSION" in memo_data:
            return "ritual"
        elif "COLLABORATION_RITUAL" in memo_data:
            return "collaboration_ritual"
        else:
            return "unknown"

    def _extract_ritual_id(self, memo_data):
        """
        Extracts ritual_id from memo_data if present.
        """
        match = re.search(r'RITUAL_SUBMISSION:(RID\d+)', memo_data)
        return match.group(1) if match else None

    def _is_valid_ritual(self, ritual_id, member_id):
        """
        Checks if a ritual_id is valid for the member_id.
        """
        valid_rituals = ["RID001", "RID002"]
        return ritual_id in valid_rituals

    def assign_task_to_user(self, task_id, user_id):
        """
        Assigns a task to a user for action or completion.

        Arguments:
        - task_id: ID of the task to assign.
        - user_id: ID of the user to whom the task is assigned.

        Returns:
        - Confirmation message of task assignment.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        assignment_log = {
            "task_id": task_id,
            "assigned_user": user_id,
            "timestamp": timestamp,
            "status": "assigned"
        }
        # Log the assignment to database or file as needed

        return f"Task {task_id} has been assigned to user {user_id}."

if __name__ == "__main__":
    db_connection = connect_to_db()
    if db_connection:
        db_connection.close()
