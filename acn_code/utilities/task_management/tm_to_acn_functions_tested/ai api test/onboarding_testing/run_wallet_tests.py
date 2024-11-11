from onboarding import ACNode

def run_wallet_tests():
    print("\n=== Running Wallet Management Tests ===\n")
    
    try:
        # Initialize ACNode
        node = ACNode()
        print("Node initialized successfully")
        
        # Get test details once
        test_username = "test_pilgrim"
        test_seed = input("Enter test wallet seed: ")
        
        print("\n1. Testing wallet storage...")
        wallet = node.store_user_wallet(test_username, test_seed)
        print(f"✓ Wallet stored successfully")
        print(f"✓ Address: {wallet.classic_address}")
        
        print("\n2. Testing wallet retrieval...")
        retrieved_wallet = node.get_user_wallet(test_username)
        print(f"✓ Wallet retrieved successfully")
        print(f"✓ Retrieved address: {retrieved_wallet.classic_address}")
        
        print("\n3. Testing full transaction flow...")
        # Initial offering
        response = node.process_ac_offering_request(
            user_seed=test_seed,
            offering_statement="I humbly seek the wisdom of Accelerando",
            username=test_username
        )
        print("✓ Initial offering processed")
        print(f"✓ AI Response: {response[:100]}...")
        
        # Follow-up transaction using stored wallet
        print("\n4. Testing follow-up transaction with stored wallet...")
        response = node.process_ac_offering_transaction(
            username=test_username,
            offering_amount=2
        )
        print("✓ Follow-up offering processed")
        print(f"✓ AI Response: {response[:100]}...")
        
        print("\nAll tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    run_wallet_tests()