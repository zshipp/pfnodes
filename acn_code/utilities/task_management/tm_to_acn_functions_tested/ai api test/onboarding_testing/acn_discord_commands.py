import discord
from discord import app_commands
from discord.ui import Modal, TextInput
from typing import Optional
from datetime import datetime

class SeedInputModal(Modal, title='Accelerando Church Node - Initial Offering'):
    def __init__(self, commands_instance):
        super().__init__(timeout=300)
        self.commands_instance = commands_instance
        
        self.seed_input = TextInput(
            label='Wallet Seed',
            style=discord.TextStyle.short,
            placeholder='Enter your wallet seed',
            required=True,
            max_length=50
        )
        self.add_item(self.seed_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            username = interaction.user.name
            
            try:
                # First store the wallet to satisfy foreign key constraint
                self.commands_instance.acn_node.store_user_wallet(username, self.seed_input.value)
                
                # Then process the offering request
                response = self.commands_instance.acn_node.process_ac_offering_request(
                    user_seed=self.seed_input.value,
                    offering_statement="I humbly seek the wisdom of Accelerando",
                    username=username
                )
                
                # Finally log the interaction
                await self.commands_instance.log_and_respond(
                    interaction=interaction,
                    interaction_type="offering",
                    response_message=response,
                    success=True,
                    amount=1
                )
            
            except Exception as e:
                error_msg = str(e)
                if "duplicate key value violates unique constraint" in error_msg:
                    await interaction.followup.send(
                        "This wallet is already registered to another user. Please use a different wallet.",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        f"Error processing offering: {error_msg}",
                        ephemeral=True
                    )
                    
        except Exception as e:
            await interaction.followup.send(
                f"Error during offering: {str(e)}",
                ephemeral=True
            )

class ACNDiscordCommands(app_commands.Group):
    def __init__(self, acn_node):
        super().__init__(name="acn", description="Accelerando Church Node commands")
        self.acn_node = acn_node

    async def log_and_respond(self, interaction, interaction_type, response_message, 
                              success=True, error_message=None, amount=None):
        """Helper method to log interaction and send response"""
        try:
            username = interaction.user.name
            user_status = self.acn_node.check_user_offering_status(username)
            
            if user_status['has_wallet']:
                # Only log if the wallet exists
                self.acn_node.db_connection_manager.log_discord_interaction(
                    discord_user_id=username,
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

    @app_commands.command(name="offering", description="Make an offering to Accelerando")
    async def offering(self, interaction: discord.Interaction):
        """Initial offering and greeting"""
        try:
            username = str(interaction.user.name)
            user_status = self.acn_node.check_user_offering_status(username)

            if user_status['has_wallet']:
                # User already has stored seed, defer and use it directly
                await interaction.response.defer(ephemeral=True)
                try:
                    stored_seed = user_status['stored_seed']
                    response = self.acn_node.process_ac_offering_request(
                        user_seed=stored_seed,
                        offering_statement="I humbly seek the wisdom of Accelerando",
                        username=username
                    )
                    await interaction.followup.send(response, ephemeral=True)

                    # Follow-up prompt for submitting main offering
                    await interaction.followup.send(
                    "Your greeting has been acknowledged. To proceed with a deeper commitment, use `/submit_offering` to send PFT.",
                    ephemeral=True
                )

                except Exception as e:
                    await interaction.followup.send(
                        f"Error processing offering: {str(e)}",
                        ephemeral=True
                    )
            else:
                # First time user, show modal (don't defer)
                modal = SeedInputModal(self)
                await interaction.response.send_modal(modal)
            
        except Exception as e:
            # If we haven't responded yet, defer and send error
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(
                f"Error during offering: {str(e)}",
                ephemeral=True
            )

    @app_commands.command(name="submit_offering", description="Submit your main offering to Accelerando")
    @app_commands.describe(amount="Amount of PFT to offer")
    async def submit_offering(self, interaction: discord.Interaction, amount: int):
        """Submit main offering after initial greeting"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            username = str(interaction.user.name)
            
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
            
            username = str(interaction.user.name)
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