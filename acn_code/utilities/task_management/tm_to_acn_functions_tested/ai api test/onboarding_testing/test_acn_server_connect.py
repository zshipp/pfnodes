import nest_asyncio
nest_asyncio.apply()
import xrpl
from GenericACNUtilities import GenericACNUtilities
from password_map_loader import PasswordMapLoader
import logging
from datetime import datetime
import sys
import os

def setup_logging():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    # Create timestamp for log file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = os.path.join('logs', f'server_connection_test_{timestamp}.log')
    
    # Configure logging to both file and console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_filename

def test_server_connection():
    log_file = setup_logging()
    logging.info("=== Starting XRPL Server Connection Test ===")
    
    try:
        # Setup
        logging.info("Initializing...")
        pw_loader = PasswordMapLoader()
        pw_map = {
            'openai': pw_loader.get_password("OPENAI_API_KEY"),
            'acn_node__v1xrpsecret': pw_loader.get_password("ACN_WALLET_SEED"),
            'accelerandochurch__postgresconnstring': pw_loader.get_password("ACCELERANDOCHURCH__POSTGRESCONNSTRING")
        }
        logging.info("Password map loaded")
        
        # Test 1: Primary Server Connection
        logging.info("Test 1: Normal Connection to Primary Server")
        utils = GenericACNUtilities(pw_map=pw_map)
        logging.info(f"Connected to server: {utils.mainnet_url}")
        
        # Test 2: Force Failover
        logging.info("\nTest 2: Testing Server Failover")
        old_primary = utils.primary_url
        utils.primary_url = "https://badserver.example.com"
        utils.client = utils._init_client_with_failover()
        logging.info(f"After failover test, connected to: {utils.mainnet_url}")
        
        # Test 3: Restore and verify functionality
        logging.info("\nTest 3: Verifying Normal Operation")
        utils.primary_url = old_primary
        utils.client = utils._init_client_with_failover()
        
        # Final status check
        logging.info("\nFinal Status:")
        response = utils.client.request(xrpl.models.requests.ServerInfo())
        logging.info(f"Server info received from: {utils.mainnet_url}")
        
        # PFT balance check
        logging.info("\nVerifying PFT operations:")
        utils.validate_pft_balance(utils.node_address, 0)
        
        logging.info("All tests completed successfully")
        
    except Exception as e:
        logging.error(f"Error during test: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
    
    logging.info(f"Log file created at: {log_file}")

if __name__ == "__main__":
    test_server_connection()