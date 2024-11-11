import asyncio
import nest_asyncio
from acn_discord_commands import ACNDiscordCommands
from onboarding import ACNode
import discord
from datetime import datetime

nest_asyncio.apply()

class SimpleTestInteraction:
    """Minimal mock interaction for testing"""
    def __init__(self, user_id):
        self.user = type('User', (), {'id': user_id})
        self.response_message = None
        
    async def defer(self, ephemeral=True):
        return True
        
    async def send(self, content, ephemeral=True):
        print(f"\nDiscord Response: {content}")  # Print full response
        self.response_message = content
        return True
        
    response = type('Response', (), {'defer': defer})()
    followup = type('Followup', (), {'send': send})()

async def test_offering_command():
    """Test the basic offering command functionality"""
    print("\n=== Testing ACN Offering Command ===")
    
    # Initialize
    node = ACNode()
    commands = ACNDiscordCommands(node)
    
    # Test data
    test_user_id = "test_pilgrim_1"
    test_seed = "snoPBrXtMeMyMHUVTgbuqAfg1SUTb"
    
    print("\n1. Testing wallet creation and initial offering:")
    
    # First, store the wallet directly
    print("\nAttempting to store wallet...")
    try:
        wallet = node.store_user_wallet(test_user_id, test_seed)
        print(f"Wallet stored successfully: {wallet.classic_address}")
    except Exception as e:
        print(f"Error storing wallet: {str(e)}")
        return
    
    # Then try the command
    print("\nTesting offering command...")
    interaction = SimpleTestInteraction(test_user_id)
    offering_command = commands.get_command("offering")
    
    if offering_command:
        try:
            await offering_command.callback(commands, interaction, seed=test_seed)
            print(f"Command completed. Response: {interaction.response_message}")
        except Exception as e:
            print(f"\nFull error in offering command: {str(e)}")
            import traceback
            print(traceback.format_exc())
        
        # Check database for logs
        try:
            logs = node.db_connection_manager.get_user_interaction_history(test_user_id)
            print("\nDatabase Logs:")
            print(logs)
            
            # Show full log entry details
            if not logs.empty:
                print("\nDetailed log entry:")
                for col in logs.columns:
                    print(f"{col}: {logs.iloc[0][col]}")
            
        except Exception as e:
            print(f"Error checking logs: {str(e)}")

if __name__ == "__main__":
    print("Starting ACN Offering Command Test...")
    asyncio.run(test_offering_command())