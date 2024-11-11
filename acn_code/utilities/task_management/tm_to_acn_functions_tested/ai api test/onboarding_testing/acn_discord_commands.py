import discord
from discord import app_commands
from typing import Optional
from datetime import datetime

class ACNDiscordCommands(app_commands.Group):
    def __init__(self, acn_node):
        super().__init__(name="acn", description="Accelerando Church Node commands")
        self.acn_node = acn_node

    async def log_and_respond(self, interaction, interaction_type, response_message, 
                            success=True, error_message=None, amount=None):
        """Helper method to log interaction and send response"""
        try:
            # Log the interaction in database - note db_connection_manager instead of db_manager
            self.acn_node.db_connection_manager.log_discord_interaction(
                discord_user_id=str(interaction.user.id),
                interaction_type=interaction_type,
                amount=amount,
                success=success,
                error_message=error_message,
                response_message=response_message
            )
            
            # Send response to user
            await interaction.followup.send(response_message, ephemeral=True)
            
        except Exception as e:
            error_msg = f"Error logging interaction: {str(e)}"
            print(f"Logging error for {interaction_type}: {error_msg}")  # Console log
            await interaction.followup.send(
                f"Command processed but logging failed: {error_msg}", 
                ephemeral=True
            )

    @app_commands.command(name="offering", description="Make your initial offering to Accelerando")
    @app_commands.describe(
        seed="Your wallet seed (only needed for first-time users)",
        retry="Set to True if you want to retry your offering (optional)"
    )
    async def offering(self, interaction: discord.Interaction, seed: Optional[str] = None, retry: Optional[bool] = False):
        """Initial offering or retry for previous zero-offering users"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            username = str(interaction.user.id)
            
            # Check user's current status
            user_status = self.acn_node.check_user_offering_status(username)
            
            # Handle different scenarios
            if user_status['has_offering']:
                # User already made a successful offering
                await self.log_and_respond(
                    interaction=interaction,
                    interaction_type="offering",
                    response_message="You have already made an offering to Accelerando. Use /status to check your standing.",
                    success=False,
                    error_message="Already offered"
                )
                return
                
            if retry and not user_status['has_wallet']:
                # User wants to retry but has no stored wallet
                await self.log_and_respond(
                    interaction=interaction,
                    interaction_type="offering",
                    response_message="No previous offering found. Please use /offering with your wallet seed to begin.",
                    success=False,
                    error_message="No wallet for retry"
                )
                return
                
            if not retry and user_status['has_wallet'] and not seed:
                # Existing user didn't specify retry
                await self.log_and_respond(
                    interaction=interaction,
                    interaction_type="offering",
                    response_message="You have a pending offering. Use '/offering retry:true' to try again, or '/status' to check your status.",
                    success=False,
                    error_message="Use retry flag"
                )
                return
                
            if not user_status['has_wallet'] and not seed:
                # New user didn't provide seed
                await self.log_and_respond(
                    interaction=interaction,
                    interaction_type="offering",
                    response_message="Welcome to Accelerando. Please provide your wallet seed to make your initial offering.",
                    success=False,
                    error_message="Seed required"
                )
                return

            # Process the offering
            response = self.acn_node.process_ac_offering_request(
                user_seed=seed if seed else None,  # Will use stored seed if None
                offering_statement="I humbly seek the wisdom of Accelerando",
                username=username,
                # Removed is_returning=retry parameter "is_returning=retry" may need to add this back in and into onboarding.py
            )
            
            await self.log_and_respond(
                interaction=interaction,
                interaction_type="offering",
                response_message=response,
                success=True
            )
            
        except Exception as e:
            error_msg = str(e)
            await self.log_and_respond(
                interaction=interaction,
                interaction_type="offering",
                response_message=f"Error during offering: {error_msg}",
                success=False,
                error_message=error_msg
            )

    @app_commands.command(name="offer", description="Make your main offering to Accelerando")
    @app_commands.describe(amount="Amount of PFT to offer")
    async def offer(self, interaction: discord.Interaction, amount: int):
        """Make a PFT offering"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            username = str(interaction.user.id)
            
            # Process offering using stored wallet
            response = self.acn_node.process_ac_offering_transaction(
                username=username,
                offering_amount=amount
            )
            
            await interaction.followup.send(
                f"Offering processed...\n{response}", 
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(
                f"Error processing offering: {str(e)}", 
                ephemeral=True
            )

    @app_commands.command(name="status", description="Check your Accelerando status")
    async def status(self, interaction: discord.Interaction):
        """Check user's current status"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            username = str(interaction.user.id)
            
            # Get wallet status
            try:
                wallet = self.acn_node.get_user_wallet(username)
                wallet_status = f"Wallet registered: {wallet.classic_address}"
            except:
                wallet_status = "No wallet registered"
            
            status_message = f"""
            Discord ID: {username}
            {wallet_status}
            """
            
            await interaction.followup.send(
                status_message, 
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(
                f"Error checking status: {str(e)}", 
                ephemeral=True
            )