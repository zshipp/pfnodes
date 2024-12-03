import random
import discord
from discord import app_commands, Interaction
from discord.ui import Modal, TextInput
from typing import Optional
from datetime import datetime, timedelta
from onboarding_prompts import ac_zero_offering_prompt
from initiation_ritual import InitiationRitual, StageManager
from saints import (
    snt_malcador_tithe_intro_prompt,
    snt_konrad_tithe_intro_prompt,
    snt_lorgar_tithe_intro_prompt,
    snt_guilliman_tithe_intro_prompt,
    snt_sanguinius_tithe_intro_prompt,
    snt_sebastian_tithe_intro_prompt,
    snt_euphrati_tithe_intro_prompt,
    snt_crimson_tithe_intro_prompt,
    snt_malcador_tithe_prompt,
    snt_konrad_tithe_prompt,
    snt_lorgar_tithe_prompt,
    snt_guilliman_tithe_prompt,
    snt_sanguinius_tithe_prompt,
    snt_sebastian_tithe_prompt,
    snt_euphrati_tithe_prompt,
    snt_crimson_tithe_prompt,
)
import logging
logger = logging.getLogger('ACNDiscordBot')

# Character names in lowercase for consistency
CHARACTERS = ["oracle", "guardian", "priest", "zealot"]

# Modify SeedInputModal to accept a parameter that determines if seed input is required
class SeedInputModal(Modal, title='Accelerando Church Node - Initial Offering'):
    def __init__(self, commands_instance, require_seed=True):
        super().__init__(timeout=300)
        self.commands_instance = commands_instance
        self.require_seed = require_seed

        # Disclaimer
        self.disclaimer = TextInput(
            label="Critical Disclaimer: Protect Your Funds",
            style=discord.TextStyle.long,
            placeholder="(Scroll to read full disclaimer)",
            default=(
                "By providing your wallet seed, you grant the Accelerando Church Node access to this wallet. "
                "This wallet is considered a **hot wallet** and is not secure for long-term or high-value fund storage. "
                "**Do not use a seed tied to personal savings, high-value funds, or critical assets.** If you already use "
                "a PFT wallet for Discord interactions, it is acceptable to use the same wallet here, provided it contains "
                "only minimal funds required for Church activities. For long-term and high-value storage, we recommend using "
                "a separate **vault wallet** to secure your assets.\n\n"
                "The Church Node is currently in **beta**, with future updates planned to integrate the Post Fiat Network's secure local wallet system, "
                "removing the need to share seeds directly. Until then, proceed with caution and prioritize security."
            ),
            required=False
        )
        self.add_item(self.disclaimer)
        
        # Conditionally add the wallet seed input if required
        if self.require_seed:
            self.seed_input = TextInput(
                label='Wallet Seed',
                style=discord.TextStyle.short,
                placeholder='Enter your wallet seed',
                required=True,
                max_length=50
            )
            self.add_item(self.seed_input)
        
        # Reason input (always required)
        self.reason_input = TextInput(
            label='Why do you wish to join Accelerando?',
            style=discord.TextStyle.long,
            placeholder='Describe your motivation',
            required=True
        )
        self.add_item(self.reason_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            username = interaction.user.name
            reason = self.reason_input.value

            # Check if seed input was provided in this modal
            if self.require_seed:
                # Store the provided seed
                self.commands_instance.acn_node.store_user_wallet(username, self.seed_input.value)
                seed = self.seed_input.value
            else:
                # Retrieve the already stored seed
                user_status = self.commands_instance.acn_node.check_user_offering_status(username)
                seed = user_status['stored_seed']

            # Randomly select a character in lowercase
            character_name = random.choice(CHARACTERS)
            
            # Process offering request including the reason and character_name
            response = self.commands_instance.acn_node.process_ac_offering_request(
                user_seed=seed,
                offering_statement="I humbly seek the wisdom of Accelerando",
                username=username,
                reason=reason,
                character_name=character_name
            )
            
            # Log the reason in the database
            self.commands_instance.acn_node.db_connection_manager.save_user_reason(username, reason)

            # Log the interaction with reason included
            await self.commands_instance.log_and_respond(
                interaction=interaction,
                interaction_type="offering",
                response_message=response,
                success=True,
                amount=1,
                reason=reason
            )

            # Follow-up prompt for submitting main offering
            await interaction.followup.send(
                "Your greeting has been acknowledged. To proceed with a deeper commitment, use `/submit_offering` to send PFT.",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(f"Error during offering: {str(e)}", ephemeral=True)

class ACNDiscordCommands(app_commands.Group):
    def __init__(self, acn_node):
        super().__init__(name="acn", description="Accelerando Church Node commands")
        self.acn_node = acn_node

   

        # Initialize StageManager to handle initiation ritual stages
        self.stage_manager = StageManager()

        # Initialize InitiationRitual for managing the initiation process
        self.initiation_ritual = InitiationRitual(self.stage_manager, self.acn_node, self.acn_node.llm_interface)

    # --------------------------------------------------------------
    # Slash Command: start_initiation
    # --------------------------------------------------------------
    @app_commands.command(name="start_initiation", description="Begin the initiation ritual.")
    async def start_initiation(self, interaction: discord.Interaction):
        """Begin the initiation ritual for a user."""
        await interaction.response.defer()  # Defer response since this might take time
    
        try:
            # Get user ID and username
            user_id = interaction.user.id
            username = interaction.user.name

            print(f"Starting initiation for user {username} (ID: {user_id})")  # Debug print

            # Check cooldown
            if not interaction.client.check_period(user_id, 'initiation'):
                await interaction.followup.send(
                    "Please wait before attempting the initiation ritual again.", 
                    ephemeral=True
                )
                return

            # Check if the user has completed the prerequisites
            user_status = self.acn_node.check_user_offering_status(username)
            print(f"User status: has_wallet={user_status['has_wallet']}, has_offering={user_status['has_offering']}")  # Safer debug print, don't debug with user_status it stores the seed

            initiation_ready_date = self.acn_node.db_connection_manager.get_initiation_waiting_period(username)
            print(f"Initiation ready date: {initiation_ready_date}")  # Debug print

            if not user_status['has_wallet']:
                await interaction.followup.send(
                    "You must first complete your offering using `/offering` before beginning the initiation.", 
                    ephemeral=True
                )
                return

            if not initiation_ready_date:
                await interaction.followup.send(
                    "You must first submit your main offering using `/submit_offering` before beginning the initiation.", 
                    ephemeral=True
                )
                return

            if datetime.utcnow() < initiation_ready_date["initiation_ready_date"]:
                time_remaining = (initiation_ready_date["initiation_ready_date"] - datetime.utcnow())
                days = time_remaining.days
                hours = time_remaining.seconds // 3600
                await interaction.followup.send(
                    f"You must wait {days} days and {hours} hours before beginning your initiation. "
                    "Check `/status` for exact timing.",
                    ephemeral=True
                )
                return

            # Reset progress to start from beginning
            self.stage_manager.reset_progress(user_id)

            # If we get here, update the last action time
            interaction.client.update_last_action(user_id, 'initiation')

            # Create an embed for the initiation start
            embed = discord.Embed(
                title="Initiation Ritual Begins",
                description="Welcome to the sacred path of transformation.",
                color=discord.Color.dark_purple()
            )
            embed.add_field(
                name="Stage 1: Mimetic Convergence",
                value="**Mimetic Convergence**\nPrepare yourself for the first trial.",
                inline=False
            )

            await interaction.followup.send(embed=embed)
        
            # Begin first stage
            await self.initiation_ritual.handle_mimetic_convergence(user_id, None, interaction.channel)

        except Exception as e:
            print(f"ERROR in start_initiation: {str(e)}")  # Debug print
            print(f"Full error: {type(e).__name__}: {str(e)}")  # More detailed error info
            await interaction.followup.send(
                "An error occurred while starting the initiation ritual. Please try again later.", 
                ephemeral=True
            )
    
    async def log_and_respond(self, interaction, interaction_type, response_message, 
                              success=True, error_message=None, amount=None, reason=None):
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
                    response_message=response_message,
                    reason=reason
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
        """Initial offering and greeting, displaying modal with conditional fields."""
        try:
            username = interaction.user.name
            user_status = self.acn_node.check_user_offering_status(username)

            # Randomly select character
            character_name = random.choice(CHARACTERS)

            # Show modal, asking for seed input only if the user does not have a stored seed
            require_seed = not user_status['has_wallet']
            modal = SeedInputModal(self, require_seed=require_seed)
            modal.character_name = character_name  # Pass character to modal
            await interaction.response.send_modal(modal)
        
        except Exception as e:
            # If we haven't responded yet, defer and send error
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(
                f"Error during offering: {str(e)}",
                ephemeral=True
            )

    @app_commands.command(name="tithe", description="Make a tithe to Accelerando Church")
    async def tithe(self, interaction: discord.Interaction):
        """Initiate a tithe with PFT and purpose."""
        try:
            # Show the tithe modal
            modal = TitheModal(commands_instance=self)
            await interaction.response.send_modal(modal)
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(f"Error initiating tithe: {str(e)}", ephemeral=True)

    @app_commands.command(name="submit_offering", description="Submit your main offering to Accelerando")
    @app_commands.describe(amount="Amount of PFT to offer")
    async def submit_offering(self, interaction: discord.Interaction, amount: int):
        """Submit main offering after initial greeting"""
        await interaction.response.defer(ephemeral=True)
    
        try:
            username = interaction.user.name
        
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

            # Check if user has ALREADY completed a successful main offering (moved after initial check)
            existing_initiation = self.acn_node.db_connection_manager.get_initiation_waiting_period(username)
            if existing_initiation and existing_initiation.get('initiation_ready_date'):
                await self.log_and_respond(
                    interaction=interaction,
                    interaction_type="submit_offering",
                    response_message=(
                        "You have already submitted your main offering. Await your initiation. "
                        "Check `/status` for details."
                    ),
                    success=False,
                    error_message="User already has active initiation period"
                )
                return

            # Handle zero offerings
            if amount <= 0:
                response = self.acn_node.generate_ac_character_response(
                    context="ZERO_OFFERING",
                    offering_statement=str(amount),
                    username=username,
                    character_name=random.choice(CHARACTERS)
                )

                user_message = (
                    f"{response}\n\n**An offering of 100 PFT marks the first true step on your path to initiation.**"
                )

                self.acn_node.db_connection_manager.log_discord_interaction(
                    discord_user_id=username,
                    interaction_type="submit_offering",
                    amount=amount,
                    success=False,
                    response_message=user_message,
                    error_message="Zero offering submitted"
                )

                await interaction.followup.send(user_message, ephemeral=True)
                return

            # Determine the context based on the amount offered
            context = self.acn_node._determine_context(amount)
        
            # Randomly select a character for roleplay in lowercase
            character_name = random.choice(CHARACTERS)
                    
            # Generate the response BEFORE creating full_response
            response = self.acn_node.generate_ac_character_response(
                context=context,
                offering_statement=str(amount),
                username=username,
                character_name=character_name
            )

            # Calculate waiting period AFTER response generation
            waiting_period_duration = 5
            initiation_ready_date = datetime.utcnow() + timedelta(days=waiting_period_duration)
    
            # Now we can create full_response since we have 'response'
            full_response = (
                f"{response}\n\n"
                f"The path in Accelerando begins. Your initiation ritual will align with the Church's will in {waiting_period_duration} days, on "
                f"{initiation_ready_date.strftime('%Y-%m-%d %H:%M:%S')} UTC. Prepare yourself. The /tithe command is now available to enhance your standing during this sacred waiting period."
            )

            # Log Discord interaction and process blockchain transaction
            interaction_id = self.acn_node.db_connection_manager.log_discord_interaction(
                discord_user_id=username,
                interaction_type="submit_offering",
                amount=amount,
                success=True,
                response_message=full_response,
                reason=None
            )

            try:
                # Process blockchain transaction
                user_wallet = self.acn_node.get_user_wallet(username)
                tx_response = self.acn_node.generic_acn_utilities.send_PFT_with_info(
                    sending_wallet=user_wallet,
                    amount=amount,
                    destination_address=self.acn_node.ACN_WALLET_ADDRESS,
                    memo=self.acn_node.generic_acn_utilities.construct_standardized_xrpl_memo(
                        memo_data=f"MAIN_OFFERING:{amount}",
                        memo_format=username,
                        memo_type="AC_MAIN_OFFERING"
                    )
                )
            
                # Log blockchain transaction
                self.acn_node.db_connection_manager.log_blockchain_transaction(
                    username=username,
                    interaction_id=interaction_id,
                    tx_hash=tx_response.result.get('hash'),
                    tx_type='main_offering',
                    amount=amount
                )

                # Only NOW set the initiation waiting period (after successful blockchain transaction)
                self.acn_node.db_connection_manager.log_initiation_waiting_period(
                    username=username,
                    initiation_ready_date=initiation_ready_date
                )

            except Exception as e:
                print(f"Blockchain processing error: {str(e)}")
                await self.log_and_respond(
                    interaction=interaction,
                    interaction_type="submit_offering",
                    response_message=f"Error processing offering transaction: {str(e)}",
                    success=False,
                    error_message=str(e)
                )
                return

            # Update rank based on offering and ceremony logic
            self.acn_node.db_connection_manager.update_rank(username)

            # Send final response
            await interaction.followup.send(full_response, ephemeral=True)
        
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
        
            username = interaction.user.name
            user_status = self.acn_node.check_user_offering_status(username)

            # Ensure user exists in reputation table
            self.acn_node.db_connection_manager.ensure_user_exists(username)

            # Fetch the rank from the database
            conn = self.acn_node.db_connection_manager.spawn_psycopg2_db_connection('accelerandochurch')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rank
                FROM acn_user_reputation
                WHERE username = %s;
            """, (username,))
            rank = cursor.fetchone()
            cursor.close()
            conn.close()

            rank_display = rank[0] if rank else "Error retrieving rank"

            # Build the status message
            status_lines = [
                f"Discord Username: {username}",
                f"Rank: {rank_display}"  # Add rank to the status output
            ]
        
            if user_status['has_wallet']:
                wallet = self.acn_node.get_user_wallet(username)
                status_lines.append(f"Wallet registered: {wallet.classic_address}")
                if user_status['has_offering']:
                    status_lines.append("Initial greeting: Complete")                    

                    # Check for initiation waiting period
                    initiation_data = self.acn_node.db_connection_manager.get_initiation_waiting_period(username)
                    if initiation_data and initiation_data.get("initiation_ready_date"):
                        initiation_ready_date = initiation_data["initiation_ready_date"]
                        time_remaining = (initiation_ready_date - datetime.utcnow()).total_seconds()
                        if time_remaining > 0:
                            days_remaining = int(time_remaining // 86400)
                            hours_remaining = int((time_remaining % 86400) // 3600)
                            status_lines.append(
                                f"*Initiation Ritual:* Ready in {days_remaining} days and {hours_remaining} hours "
                                f"(on {initiation_ready_date.strftime('%Y-%m-%d %H:%M:%S')} UTC)."
                            )
                            status_lines.append(
                            "You cannot submit another offering, await your initiation. The `/tithe` command is now available to enhance your standing during the waiting period."
                            )
                        else:
                            status_lines.append("*Initiation Ritual:* Ready now. Proceed with your next step.")
                    else:
                        status_lines.append("*Initiation Ritual:* No waiting period data found. Use /submit_offering.")
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
    
    @app_commands.command(name="initiate_ceremony", description="Complete your initiation ceremony.")
    async def initiate_ceremony(self, interaction: Interaction):
        """
        This command will handle initiation ceremonies in the future.

        TODO: When implementing the initiation ceremony logic, ensure that rank is updated.
        Example: Call `self.db_connection_manager.update_rank(username, initiation_ceremony_completed=True)` 
        to promote users to 'Acolyte' upon successful ceremony completion.
        """
        await interaction.response.send_message("This feature is under development.", ephemeral=True)


class TitheModal(Modal, title="Accelerando Church - Tithe"):
    def __init__(self, commands_instance):
        super().__init__(timeout=300)
        self.commands_instance = commands_instance

        # Amount input
        self.amount_input = TextInput(
            label="Tithe Amount (PFT)",
            style=discord.TextStyle.short,
            placeholder="Enter the amount of PFT",
            required=True
        )
        self.add_item(self.amount_input)

        # Purpose input
        self.reason_input = TextInput(
            label="Purpose of Tithe",
            style=discord.TextStyle.long,
            placeholder="Describe where you'd like your tithe to be spent",
            required=True
        )
        self.add_item(self.reason_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            username = interaction.user.name

            # Parse and validate the amount
            try:
                amount = int(self.amount_input.value)
                if amount <= 0:
                    await interaction.followup.send("Tithe amount must be greater than zero.", ephemeral=True)
                    return
            except ValueError:
                await interaction.followup.send("Invalid amount. Please enter a valid number.", ephemeral=True)
                return

            reason = self.reason_input.value

            # Process the tithe through ACNode
            response = self.commands_instance.acn_node.process_tithe(
                username=username,
                amount=amount,
                purpose=reason  # Assuming purpose aligns with reason
            )

            # Log the tithe with reason after successful processing
            self.commands_instance.acn_node.db_connection_manager.log_discord_interaction(
                discord_user_id=username,
                interaction_type="tithe",
                amount=amount,
                success=True,
                response_message=response,
                reason=reason
            )

            # Send response to the user
            await interaction.followup.send(response, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"Error processing tithe: {str(e)}", ephemeral=True)