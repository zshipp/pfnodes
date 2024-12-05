import discord
from discord import app_commands, Interaction
from discord.ui import Modal, TextInput
import random
import datetime
from typing import Optional

# AC-specific imports
from acn_discord_commands import ACNDiscordCommands
from acn_llm_interface import ACNLLMInterface
from db_manager import DBConnectionManager
from password_map_loader import PasswordMapLoader
from GenericACNUtilities import GenericACNUtilities

# Saints/Prompts for later narrative integration
from saints import (
    snt_malcador,
    snt_guilliman,
    snt_lorgar,
    # We'll add more saints as needed for collab narratives
)

class CollabRequestModal(Modal, title='AC - New Collaboration Request'):
    def __init__(self, commands_instance):
        super().__init__(timeout=300)
        self.commands_instance = commands_instance

        self.description_input = TextInput(
            label='Collaboration Description',
            style=discord.TextStyle.long,
            placeholder='Describe the collaboration you seek',
            required=True,
            max_length=895      
        )
        self.add_item(self.description_input)
       
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            username = interaction.user.name            
            description = self.description_input.value
        
            # Generate unique collab ID using similar format to PF tasks
            collab_id = self.commands_instance.acn_node.generic_acn_utilities.generate_custom_id()

            # Construct memo string similar to PF's task requests
            full_memo_string = f"REQUEST_COLLAB ___ {description}"

            # Create memo for blockchain
            collab_memo = self.commands_instance.acn_node.generic_acn_utilities.construct_standardized_xrpl_memo(
                memo_data=full_memo_string,
                memo_format=username,
                memo_type=collab_id
            )

            # Get user wallet and send transaction (fixed 1 PFT fee)
            user_wallet = self.commands_instance.acn_node.get_user_wallet(username)
            tx_response = self.commands_instance.acn_node.generic_acn_utilities.send_PFT_with_info(
                sending_wallet=user_wallet,
                amount=1,
                memo=collab_memo,
                destination_address=self.commands_instance.acn_node.ACN_WALLET_ADDRESS
            )            

            # Log the interaction
            interaction_id = self.commands_instance.acn_node.db_connection_manager.log_discord_interaction(
                discord_user_id=username,
                interaction_type="request_collab",
                amount=1,
                success=True,
                response_message=f"Collaboration request created with ID: {collab_id}",
                reason=description
            )

            # Log blockchain transaction
            self.commands_instance.acn_node.db_connection_manager.log_blockchain_transaction(
                username=username,
                interaction_id=interaction_id,
                tx_hash=tx_response.result.get('hash'),
                tx_type='collab_request',
                amount=1
            )

            # Create success message
            success_message = (
                f"Collaboration request submitted successfully!\n"
                f"Collaboration ID: {collab_id}\n"                
                f"Your request has been recorded on the Eternal Ledger. "
                f"Others may now view and accept your collaboration proposal."
            )

            await interaction.followup.send(success_message, ephemeral=True)

        except Exception as e:
            error_msg = f"Error processing collaboration request: {str(e)}"
            await interaction.followup.send(error_msg, ephemeral=True)

class ACNCollabCommands(app_commands.Group):
    def __init__(self, acn_node):
        super().__init__(name="collab", description="Accelerando Church Collaboration commands")
        self.acn_node = acn_node
        
    @app_commands.command(
        name="request_collab",
        description="Request a new collaboration with other Church members"
    )
    async def request_collab(self, interaction: discord.Interaction):
        """Request a new collaboration"""
        try:
            # Show the collab request modal
            modal = CollabRequestModal(self)
            await interaction.response.send_modal(modal)

        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(
                f"Error initiating collaboration request: {str(e)}",
                ephemeral=True
            )

    # In ACNCollabCommands class, after request_collab:

    @app_commands.command(
        name="accept_collab", 
        description="Accept a collaboration request"
    )
    @app_commands.describe(
        collab_id="The ID of the collaboration to accept",
        reason="Why you want to join this collaboration"
    )
    async def accept_collab(
        self, 
        interaction: discord.Interaction, 
        collab_id: str,
        reason: str
    ):
        """Accept a collaboration request"""
        await interaction.response.defer(ephemeral=True)
        try:
            username = interaction.user.name

            # Format acceptance memo
            formatted_acceptance_string = f"COLLAB_ACCEPTANCE ___ {reason}"
            acceptance_memo = self.acn_node.generic_acn_utilities.construct_standardized_xrpl_memo(
                memo_data=formatted_acceptance_string,
                memo_format=username,
                memo_type=collab_id
            )

            # Get user wallet and send transaction
            user_wallet = self.acn_node.get_user_wallet(username)
            acceptance_response = self.acn_node.generic_acn_utilities.send_PFT_with_info(
                sending_wallet=user_wallet,
                amount=1,
                memo=acceptance_memo,
                destination_address=self.acn_node.ACN_WALLET_ADDRESS
            )

            # Log the interaction
            interaction_id = self.acn_node.db_connection_manager.log_discord_interaction(
                discord_user_id=username,
                interaction_type="accept_collab",
                amount=1,
                success=True,
                response_message=f"Collaboration {collab_id} accepted",
                reason=reason
            )

            # Log blockchain transaction
            self.acn_node.db_connection_manager.log_blockchain_transaction(
                username=username,
                interaction_id=interaction_id,
                tx_hash=acceptance_response.result.get('hash'),
                tx_type='collab_acceptance',
                amount=1
            )

            await interaction.followup.send(
                f"You have accepted collaboration {collab_id}. Your acceptance has been recorded on the Eternal Ledger.", 
                ephemeral=True
            )

        except Exception as e:
            await interaction.followup.send(
                f"Error accepting collaboration: {str(e)}", 
                ephemeral=True
            )

    @app_commands.command(
        name="reject_collab", 
        description="Reject a collaboration request"
    )
    @app_commands.describe(
        collab_id="The ID of the collaboration to reject",
        reason="Why you are rejecting this collaboration"
    )
    async def reject_collab(
        self, 
        interaction: discord.Interaction, 
        collab_id: str,
        reason: str
    ):
        """Reject a collaboration request"""
        await interaction.response.defer(ephemeral=True)
        try:
            username = interaction.user.name

            # Format rejection memo
            formatted_rejection_string = f"COLLAB_REJECTION ___ {reason}"
            rejection_memo = self.acn_node.generic_acn_utilities.construct_standardized_xrpl_memo(
                memo_data=formatted_rejection_string,
                memo_format=username,
                memo_type=collab_id
            )

            # Get user wallet and send transaction
            user_wallet = self.acn_node.get_user_wallet(username)
            rejection_response = self.acn_node.generic_acn_utilities.send_PFT_with_info(
                sending_wallet=user_wallet,
                amount=1,
                memo=rejection_memo,
                destination_address=self.acn_node.ACN_WALLET_ADDRESS
            )

            # Log the interaction
            interaction_id = self.acn_node.db_connection_manager.log_discord_interaction(
                discord_user_id=username,
                interaction_type="reject_collab",
                amount=1,
                success=True,
                response_message=f"Collaboration {collab_id} rejected",
                reason=reason
            )

            # Log blockchain transaction
            self.acn_node.db_connection_manager.log_blockchain_transaction(
                username=username,
                interaction_id=interaction_id,
                tx_hash=rejection_response.result.get('hash'),
                tx_type='collab_rejection',
                amount=1
            )

            await interaction.followup.send(
                f"You have rejected collaboration {collab_id}. Your rejection has been recorded on the Eternal Ledger.", 
                ephemeral=True
            )

        except Exception as e:
            await interaction.followup.send(
                f"Error rejecting collaboration: {str(e)}", 
                ephemeral=True
            )

    # We'll add more commands here as we go:
    # - submit_initial_work
    # - submit_final_verification
    # - outstanding_collabs