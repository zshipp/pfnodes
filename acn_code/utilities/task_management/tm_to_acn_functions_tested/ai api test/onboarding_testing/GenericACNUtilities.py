import xrpl
import binascii
from xrpl.wallet import Wallet
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment, Memo
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.utils import xrp_to_drops
import json
import datetime
import nest_asyncio
nest_asyncio.apply()

class GenericACNUtilities:
    def __init__(self, pw_map, node_name='accelerandochurch'):
        self.pw_map = pw_map
        self.pft_issuer = 'rnQUEEg8yyjrwk9FhyXpKavHyCRJM9BDMW'
        self.primary_url = "https://xrplcluster.com"
        self.backup_url = "https://s2.ripple.com:51234"
        self.mainnet_url = self.primary_url  # Start with primary
        self.node_name = node_name
        self.node_address = "rpb7dex8DMLRXunDcTbbQeteCCYcyo9uSd"
        self.node_seed = self.pw_map['acn_node__v1xrpsecret']
        
        # Initialize client with failover support
        self.client = self._init_client_with_failover()
        
        # Initialize node wallet with error handling
        try:
            self.node_wallet = self.spawn_user_wallet_from_seed(self.node_seed)
            print(f"Initialized {node_name} node wallet: {self.node_wallet.classic_address}")
        except Exception as e:
            raise Exception(f"Failed to initialize node wallet: {str(e)}")
                
        # Verify PFT trust line exists
        try:
            if self._verify_trust_line():
                print("PFT trust line verified")
            else:
                print("Warning: No PFT trust line found for node wallet")
        except Exception as e:
            print(f"Trust line verification failed: {str(e)}")

    def _init_client_with_failover(self):
        """Initialize client with failover support"""
        # Try primary first
        try:
            print(f"Attempting connection to primary server: {self.mainnet_url}")
            client = JsonRpcClient(self.mainnet_url)
            client.request(xrpl.models.requests.ServerInfo())
            print(f"Connected successfully to primary server")
            return client
        except Exception as e:
            print(f"Primary server failed: {str(e)}")
            
            # Try backup
            try:
                print(f"Attempting connection to backup server: {self.backup_url}")
                self.mainnet_url = self.backup_url  # Switch to backup URL
                client = JsonRpcClient(self.mainnet_url)
                client.request(xrpl.models.requests.ServerInfo())
                print(f"Connected successfully to backup server")
                return client
            except Exception as e:
                raise Exception(f"Both primary and backup servers failed. Last error: {str(e)}")

    def _verify_trust_line(self):
        """Verify PFT trust line exists for node wallet"""
        try:
            return self.validate_pft_balance(self.node_wallet.classic_address, 0)
        except Exception as e:
            print(f"Trust line verification failed: {str(e)}")
            return False

    def validate_pft_balance(self, address, minimum_balance):
        """Validates if an address has sufficient PFT balance"""
        try:
            print(f"\nChecking PFT balance for {address}")
            response = self.client.request(xrpl.models.requests.AccountLines(
                account=address,
                ledger_index="validated"
            ))
            
            for line in response.result.get("lines", []):
                if line.get("currency") == "PFT" and line.get("account") == self.pft_issuer:
                    balance = float(line.get("balance", 0))
                    print(f"Current PFT balance: {balance}")
                    if balance >= minimum_balance:
                        print("Balance sufficient")
                        return True
                    else:
                        print(f"Insufficient balance: {balance} < {minimum_balance}")
                        return False
                        
            print("No PFT trust line found")
            return False
            
        except Exception as e:
            print(f"Balance check failed: {str(e)}")
            return False

    def log_transaction(self, tx_type, sender, amount, result):
        """Log XRPL transaction details"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = {
                'timestamp': timestamp,
                'type': tx_type,
                'sender': sender,
                'amount': amount,
                'result': result
            }
            print(f"Transaction Log [{timestamp}]: {tx_type} | From: {sender} | Amount: {amount} PFT")
            if result:
                print(f"Hash: {result.get('hash', 'N/A')}")
                print(f"Status: {result.get('validated', False)}")
            
            return log_entry
        except Exception as e:
            print(f"Failed to log transaction: {str(e)}")

    def send_PFT_with_info(self, sending_wallet, amount, memo, destination_address):
        """Sends PFT tokens with memo information with failover support"""
        try:
            print(f"\nInitiating transaction of {amount} PFT")
            print(f"From: {sending_wallet.classic_address}")
            print(f"To: {destination_address}")

            # Verify PFT balance before sending
            if not self.validate_pft_balance(sending_wallet.classic_address, amount):
                raise Exception(f"Insufficient PFT balance for sending {amount} PFT")

            # Create payment
            amount_to_send = IssuedCurrencyAmount(
                currency="PFT",
                issuer=self.pft_issuer,
                value=str(amount)
            )
            
            payment = Payment(
                account=sending_wallet.classic_address,
                amount=amount_to_send,
                destination=destination_address,
                memos=[memo]
            )

            # Submit with retry on failure
            try:
                response = xrpl.transaction.submit_and_wait(
                    payment, 
                    self.client, 
                    sending_wallet,
                    check_fee=True
                )
            except Exception as e:
                print(f"Transaction failed on primary server, trying backup...")
                self.client = self._init_client_with_failover()  # Try failover
                response = xrpl.transaction.submit_and_wait(
                    payment, 
                    self.client, 
                    sending_wallet,
                    check_fee=True
                )
            
            result = response.result
            success = result.get("validated", False)
            
            # Log transaction
            self.log_transaction(
                "PFT Transfer",
                sending_wallet.classic_address,
                amount,
                result if success else None
            )

            if success:
                print(f"Transaction successful: {result['hash']}")
                return response
            else:
                raise Exception(f"Transaction failed: {result}")

        except Exception as e:
            error_msg = f"Transaction failed: {str(e)}"
            print(f"\nERROR: {error_msg}")
            raise Exception(error_msg)

    def construct_standardized_xrpl_memo(self, memo_data, memo_type, memo_format):
        """Constructs a standardized XRPL memo"""
        try:
            memo_hex = binascii.hexlify(memo_data.encode()).decode()
            memo_type_hex = binascii.hexlify(memo_type.encode()).decode()
            memo_format_hex = binascii.hexlify(memo_format.encode()).decode()
            
            memo = Memo(
                memo_data=memo_hex,
                memo_type=memo_type_hex,
                memo_format=memo_format_hex
            )
            return memo
        except Exception as e:
            raise Exception(f"Failed to construct memo: {str(e)}")

    def spawn_user_wallet_from_seed(self, seed):
        """Creates user wallet from seed"""
        try:
            wallet = Wallet.from_seed(seed)
            print(f'Wallet initialized with classic address {wallet.classic_address}')
            return wallet
        except Exception as e:
            raise Exception(f"Failed to create wallet: {str(e)}")

    def to_hex(self, string):
        """Convert string to hex"""
        return binascii.hexlify(string.encode()).decode()