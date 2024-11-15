import random
import discord
from discord import app_commands
from acn_discord_commands import ACNDiscordCommands
from onboarding import ACNode
from password_map_loader import PasswordMapLoader
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='acn_discord_bot.log'
)
logger = logging.getLogger('ACNDiscordBot')

class ACNDiscordBot(discord.Client):
    def __init__(self):
        # Initialize with required intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        
        # Command tree setup
        self.tree = app_commands.CommandTree(self)
        
        # Setup password loader and get Discord token
        self.password_loader = PasswordMapLoader()
        self.pw_map = {
            'openai': self.password_loader.get_password("OPENAI_API_KEY"),
            'discord_token': self.password_loader.get_password("DISCORD_TOKEN"),
            'acn_node__v1xrpsecret': self.password_loader.get_password("ACN_WALLET_SEED")
        }
        
        # Initialize ACNode with pw_map
        self.acn_node = ACNode()
        
        # Period tracking for rate limiting
        self.period_map = {
            'offering_cooldown': timedelta(hours=22),  # 24 hour cooldown between offerings
            'status_cooldown': timedelta(minutes=1),   # 5 minute cooldown for status checks
            'last_offering': {},  # Track last offering time per user
            'last_status': {}     # Track last status check per user
        }
        
        # Add commands group
        self.tree.add_command(ACNDiscordCommands(self.acn_node))
        
        logger.info("ACNDiscordBot initialized successfully")

    async def setup_hook(self):
        """Initial setup after bot connects"""
        try:
            await self.tree.sync()
            logger.info("Command tree synchronized")
        except Exception as e:
            logger.error(f"Failed to sync command tree: {str(e)}")
            raise

    async def on_ready(self):
        """Called when bot successfully connects"""
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        print(f'Bot connected as {self.user.name}')

    def check_period(self, user_id: str, action_type: str) -> bool:
        """Check if user is within allowed period for action"""
        current_time = datetime.now()
        last_time_map = {
            'offering': self.period_map['last_offering'],
            'status': self.period_map['last_status']
        }
        cooldown_map = {
            'offering': self.period_map['offering_cooldown'],
            'status': self.period_map['status_cooldown']
        }
        
        last_time = last_time_map[action_type].get(user_id)
        if last_time is None:
            return True
            
        cooldown = cooldown_map[action_type]
        return (current_time - last_time) > cooldown

    def update_last_action(self, user_id: str, action_type: str):
        """Update timestamp of user's last action"""
        if action_type == 'offering':
            self.period_map['last_offering'][user_id] = datetime.now()
        elif action_type == 'status':
            self.period_map['last_status'][user_id] = datetime.now()

def run_discord_bot():
    """Run the Discord bot with error handling"""
    try:
        client = ACNDiscordBot()
        client.run(client.pw_map['discord_token'])
    except Exception as e:
        logger.critical(f"Bot failed to start: {str(e)}")
        raise

if __name__ == "__main__":
    run_discord_bot()