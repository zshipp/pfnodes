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

    @app_commands.command(
        name="submit_initial_work",
        description="Submit initial work for a collaboration"
    )
    @app_commands.describe(
        collab_id="The ID of the collaboration",
        completion_details="Details about the work completed"
    )
    async def submit_initial_work(
        self,
        interaction: discord.Interaction,
        collab_id: str,
        completion_details: str
    ):
        """Submit initial work for verification"""
        await interaction.response.defer(ephemeral=True)
        try:
            username = interaction.user.name
            
            # Format submission memo
            formatted_submission = f"COLLAB_COMPLETION ___ {completion_details}"
            submission_memo = self.acn_node.generic_acn_utilities.construct_standardized_xrpl_memo(
                memo_data=formatted_submission,
                memo_format=username,
                memo_type=collab_id
            )

            # Get user wallet and send transaction
            user_wallet = self.acn_node.get_user_wallet(username)
            submission_response = self.acn_node.generic_acn_utilities.send_PFT_with_info(
                sending_wallet=user_wallet,
                amount=1,
                memo=submission_memo,
                destination_address=self.acn_node.ACN_WALLET_ADDRESS
            )

            # Log interaction
            interaction_id = self.acn_node.db_connection_manager.log_discord_interaction(
                discord_user_id=username,
                interaction_type="submit_initial_work",
                amount=1,
                success=True,
                response_message=f"Initial work submitted for {collab_id}",
                reason=completion_details
            )

            # Log blockchain transaction
            self.acn_node.db_connection_manager.log_blockchain_transaction(
                username=username,
                interaction_id=interaction_id,
                tx_hash=submission_response.result.get('hash'),
                tx_type='collab_initial_submission',
                amount=1
            )

            await interaction.followup.send(
                f"Initial work submitted for collaboration {collab_id}. Your submission has been recorded on the Eternal Ledger.",
                ephemeral=True
            )

        except Exception as e:
            await interaction.followup.send(
                f"Error submitting initial work: {str(e)}",
                ephemeral=True
            )

    @app_commands.command(
        name="submit_final_verification",
        description="Submit final verification for a collaboration"
    )
    @app_commands.describe(
        collab_id="The ID of the collaboration",
        verification_details="Verification evidence and details"
    )
    async def submit_final_verification(
        self,
        interaction: discord.Interaction,
        collab_id: str,
        verification_details: str
    ):
        """Submit final verification with evidence"""
        await interaction.response.defer(ephemeral=True)
        try:
            username = interaction.user.name
            
            # Format verification memo
            formatted_verification = f"COLLAB_VERIFICATION ___ {verification_details}"
            verification_memo = self.acn_node.generic_acn_utilities.construct_standardized_xrpl_memo(
                memo_data=formatted_verification,
                memo_format=username,
                memo_type=collab_id
            )

            # Get user wallet and send transaction
            user_wallet = self.acn_node.get_user_wallet(username)
            verification_response = self.acn_node.generic_acn_utilities.send_PFT_with_info(
                sending_wallet=user_wallet,
                amount=1,
                memo=verification_memo,
                destination_address=self.acn_node.ACN_WALLET_ADDRESS
            )

            # Log interaction
            interaction_id = self.acn_node.db_connection_manager.log_discord_interaction(
                discord_user_id=username,
                interaction_type="submit_final_verification",
                amount=1,
                success=True,
                response_message=f"Final verification submitted for {collab_id}",
                reason=verification_details
            )

            # Log blockchain transaction
            self.acn_node.db_connection_manager.log_blockchain_transaction(
                username=username,
                interaction_id=interaction_id,
                tx_hash=verification_response.result.get('hash'),
                tx_type='collab_final_verification',
                amount=1
            )

            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # TODO: PLACEHOLDER - Replace with actual AI verification
            # This should integrate with AI judging system similar to PF
            # Currently just auto-accepts all verifications
            # Needs:
            # - AI evaluation of submission
            # - Score calculation
            # - Reward distribution based on scores
            # - Proper feedback generation
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            print("WARNING: Using placeholder verification - auto-accepting all submissions!")
            
            # Placeholder response - will be replaced with AI-generated feedback
            verification_message = (
                f"Final verification submitted for collaboration {collab_id}.\n"
                f"[PLACEHOLDER] Verification auto-accepted pending AI judging implementation.\n"
                "Your verification has been recorded on the Eternal Ledger."
            )

            await interaction.followup.send(verification_message, ephemeral=True)

            await interaction.followup.send(
                f"Final verification submitted for collaboration {collab_id}. Your verification has been recorded on the Eternal Ledger.",
                ephemeral=True
            )

        except Exception as e:
            await interaction.followup.send(
                f"Error submitting final verification: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(
        name="outstanding_collabs", 
        description="View all outstanding collaborations"
    )
    async def outstanding_collabs(self, interaction: discord.Interaction):
        """Display outstanding collaborations"""
        await interaction.response.defer(ephemeral=True)
        try:
            username = interaction.user.name
            
            # Log the interaction
            self.acn_node.db_connection_manager.log_discord_interaction(
                discord_user_id=username,
                interaction_type="outstanding_collabs",
                amount=0,
                success=True,
                response_message="Requested outstanding collaborations list"
            )

            # Get all memo transactions for this user
            all_account_info = self.acn_node.generic_acn_utilities.get_memo_detail_df_for_account(
                account_address=self.acn_node.ACN_WALLET_ADDRESS, 
                pft_only=True
            )

            # Filter for collab requests that haven't been accepted/rejected
            collab_requests = all_account_info[
                all_account_info['memo_data'].apply(lambda x: 'REQUEST_COLLAB' in str(x))
            ].copy()

            if len(collab_requests) == 0:
                await interaction.followup.send(
                    "No outstanding collaborations found.", 
                    ephemeral=True
                )
                return

            # Format output message
            output = "**Outstanding Collaborations:**\n\n"
            for _, collab in collab_requests.iterrows():
                collab_id = collab['memo_type']
                description = collab['memo_data'].replace('REQUEST_COLLAB ___ ', '')
                user = collab['memo_format']
                output += f"**ID:** {collab_id}\n"
                output += f"**From:** {user}\n"
                output += f"**Description:** {description}\n"
                output += "─" * 40 + "\n\n"

            await interaction.followup.send(output, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(
                f"Error retrieving outstanding collaborations: {str(e)}", 
                ephemeral=True
            )
