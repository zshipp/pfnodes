# Verification Logic for Acceleration Church Node
## Draft 2

#### Verification Logic for Acceleration Church Node (ACN)

**Objective**: Ensure all tithe and ritual submissions on the PFT Network are securely logged, cross-verified with the member’s wallet address, and discrepancies flagged for further review. Sensitive database credentials are managed securely via `PasswordMapLoader`.

**Verification Criteria**:

1. **Tithe Verification**:
    
    - **Member ID and Wallet Address**: Each submission must include a valid `member_id` and `wallet_address`. The wallet address is cross-referenced with the registered address for the `member_id` to ensure transaction authenticity.
    - **Amount**: The submitted tithe amount must meet or exceed a specified minimum.
    - **Memo Validation**: Each tithe submission requires specific markers in the memo field (e.g., `TITHE_SUBMISSION`), parsed through code functions to verify the tithe type.
2. **Ritual Verification**:
    
    - **Member ID and Wallet Address**: Validate that the ritual log includes a valid `member_id` and verify it originates from the associated wallet address.
    - **Ritual ID**: Rituals must have a unique `ritual_id` that corresponds to a predefined ritual in the database. Valid IDs are strictly managed in the `Rituals` table.
    - **Memo Data**: Parse the memo for ritual-specific fields (e.g., `ritual_type`, `intention`) using dedicated parsing functions.
    - **Verification Conditions**: Confirm that the submission satisfies the requirements for the ritual (e.g., specific contributions, attendance counts).

**Error Handling and Discrepancies**:

- **Missing or Invalid Fields**: If any required field is missing or invalid, the submission is flagged and marked as unverified.
- **Wallet Address Mismatch**: If the submission does not come from the registered wallet address associated with the `member_id`, the submission is flagged as unverified.
- **Incorrect Amounts**: Log and flag submissions with amounts below the expected values, with an option to notify members for corrections.
- **Duplicate Submissions**: Duplicate entries (by submission ID) are flagged and logged to prevent redundancy.

**Data Flow and Process**:

1. **Submission Logging**:
    
    - Each transaction is logged in the `Submissions` table, and relevant details (`member_id`, `wallet_address`, `amount`, `timestamp`) are extracted from the memo data and verified.
2. **Cross-Verification**:
    
    - For each entry in the `Submissions` table:
        - Validate the `member_id` and `wallet_address` pairing.
        - Check that submission data aligns with predefined values in the `Rituals` and `Members` tables.
    - Record the verification status (`verified` or `unverified`) in the `Submissions` table with reasons noted for unverified statuses.
3. **Notification and Reporting**:
    
    - Generate a report summarizing unverified submissions and discrepancies for administrative review.
    - (Optional) Notify members regarding corrections on flagged submissions.

---

### Future Steps for Implementation


3. **Testing the Verification Logic**:
    
    - Test the system with various submission cases to ensure handling of valid and invalid submissions (e.g., mismatched wallets, incorrect amounts).
    - Confirm that submissions with accurate details are marked as verified, and discrepancies are flagged with appropriate reasons.