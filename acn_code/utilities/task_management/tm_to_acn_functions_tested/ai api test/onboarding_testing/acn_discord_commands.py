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
            # Log the interaction in database
            self.acn_node.db_connection_manager.log_discord_interaction(
                discord_user_id=str(interaction.user.id),
                interaction_type=interaction_type,
                amount=amount,
                success=success,
                error_message=error_message,
                response_message=response_message
            )
            
            await interaction.followup.send(response_message, ephemeral=True)
            
        except Exception as e:
            error_msg = f"Error logging interaction: {str(e)}"
            print(f"Logging error for {interaction_type}: {error_msg}")
            await interaction.followup.send(
                f"Command processed but logging failed: {error_msg}", 
                ephemeral=True
            )

    @app_commands.command(name="offering", description="Begin your journey with Accelerando")
    @app_commands.describe(
        seed="Your wallet seed (required for first contact)"
    )
    async def offering(self, interaction: discord.Interaction, seed: str):
        """Initial offering and greeting"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            username = str(interaction.user.id)
            
            # Check if user has already completed initial offering
            user_status = self.acn_node.check_user_offering_status(username)
            
            if user_status['has_offering']:
                await self.log_and_respond(
                    interaction=interaction,
                    interaction_type="offering",
                    response_message="You have already been greeted by Accelerando. Use /submit_offering to make your main offering.",
                    success=False,
                    error_message="Already greeted"
                )
                return

            # Process initial offering (1 PFT + greeting)
            response = self.acn_node.process_ac_offering_request(
                user_seed=seed,
                offering_statement="I humbly seek the wisdom of Accelerando",
                username=username
            )
            
            await self.log_and_respond(
                interaction=interaction,
                interaction_type="offering",
                response_message=response,
                success=True,
                amount=1
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

    @app_commands.command(name="submit_offering", description="Submit your main offering to Accelerando")
    @app_commands.describe(amount="Amount of PFT to offer")
    async def submit_offering(self, interaction: discord.Interaction, amount: int):
        """Submit main offering after initial greeting"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            username = str(interaction.user.id)
            
            # Verify user has completed initial offering
            user_status = self.acn_node.check_user_offering_status(username)
            
            if not user_status['has_wallet']:
                await self.log_and_respond(
                    interaction=interaction,
                    interaction_type="submit_offering",
                    response_message="You must first greet Accelerando using /offering before making your main offering.",
                    success=False,
                    error_message="No initial greeting"
                )
                return

            # Process offering using latest method signature
            response = self.acn_node.process_ac_offering_transaction(
                username=username,
                offering_amount=amount
            )
            
            await self.log_and_respond(
                interaction=interaction,
                interaction_type="submit_offering",
                response_message=response,
                success=True,
                amount=amount
            )
            
        except Exception as e:
            error_msg = str(e)
            await self.log_and_respond(
                interaction=interaction,
                interaction_type="submit_offering",
                response_message=f"Error processing offering: {error_msg}",
                success=False,
                error_message=error_msg
            )

    @app_commands.command(name="status", description="Check your Accelerando status")
    async def status(self, interaction: discord.Interaction):
        """Check user's current status"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            username = str(interaction.user.id)
            user_status = self.acn_node.check_user_offering_status(username)
            
            status_lines = [
                f"Discord ID: {username}"
            ]
            
            if user_status['has_wallet']:
                wallet = self.acn_node.get_user_wallet(username)
                status_lines.append(f"Wallet registered: {wallet.classic_address}")
                if user_status['has_offering']:
                    status_lines.append("Initial greeting: Complete")
                    status_lines.append("Ready for main offering: Yes")
                else:
                    status_lines.append("Initial greeting: Pending")
                    status_lines.append("Ready for main offering: No - Use /offering first")
            else:
                status_lines.append("No wallet registered - Use /offering to begin")
            
            status_message = "\n".join(status_lines)
            
            await self.log_and_respond(
                interaction=interaction,
                interaction_type="status",
                response_message=status_message,
                success=True
            )
            
        except Exception as e:
            error_msg = str(e)
            await interaction.followup.send(
                f"Error checking status: {error_msg}", 
                ephemeral=True
            )