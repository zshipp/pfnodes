import binascii
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class MockMemo:
    memo_data: str
    memo_type: str
    memo_format: str

@dataclass
class MockWallet:
    classic_address: str
    seed: str

@dataclass
class MockResponse:
    status: str
    transaction_hash: str
    wallet_address: str
    destination: str
    amount: str
    memo: Optional[MockMemo] = None

class GenericACNUtilities:
    def __init__(self, pw_map, node_name='accelerandochurch'):
        self.pw_map = pw_map
        self.pft_issuer = 'rnQUEEg8yyjrwk9FhyXpKavHyCRJM9BDMW'
        self.mainnet_url = "http://127.0.0.1:5005"
        self.node_name = node_name
        self.node_address = "rpb7dex8DMLRXunDcTbbQeteCCYcyo9uSd"  # Moved from ACNode
        self.node_seed = self.pw_map.get('acn_node__v1xrpsecret', 'mock_seed')
        self.node_wallet = self.spawn_user_wallet_from_seed(self.node_seed)
        print(f"Initialized {node_name} utilities with mock blockchain functionality")

    def send_PFT_with_info(self, sending_wallet, amount, memo, destination_address, url=None):
        """Simulates sending PFT tokens with memo information"""
        print(f"\nMOCK TRANSACTION:")
        print(f"From: {sending_wallet.classic_address}")
        print(f"To: {destination_address}")
        print(f"Amount: {amount} PFT")
        print(f"Memo Data: {memo.memo_data if hasattr(memo, 'memo_data') else binascii.unhexlify(memo['MemoData']).decode()}")
        
        # Create mock response
        response = MockResponse(
            status="SUCCESS",
            transaction_hash="MOCK_TX_" + binascii.hexlify(str(amount).encode()).decode()[:8],
            wallet_address=sending_wallet.classic_address,
            destination=destination_address,
            amount=str(amount)
        )
        print(f"Transaction Hash: {response.transaction_hash}")
        return response

    def construct_standardized_xrpl_memo(self, memo_data, memo_type, memo_format):
        """Constructs a mock standardized memo"""
        memo_hex = self.to_hex(memo_data)
        memo_type_hex = self.to_hex(memo_type)
        memo_format_hex = self.to_hex(memo_format)
        
        return {
            "MemoData": memo_hex,
            "MemoType": memo_type_hex,
            "MemoFormat": memo_format_hex
        }

    def spawn_user_wallet_from_seed(self, seed):
        """Creates a mock wallet from seed"""
        # Create deterministic mock address from seed
        mock_address = "r" + binascii.hexlify(seed[:10].encode()).decode()
        wallet = MockWallet(classic_address=mock_address, seed=seed)
        print(f'Mock wallet created with classic address: {wallet.classic_address}')
        return wallet

    def to_hex(self, string):
        """Convert string to hex"""
        return binascii.hexlify(string.encode()).decode()