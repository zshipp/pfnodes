import random
from ai_judging import AIJudgingWorkflow, evaluate_renunciation, evaluate_credo_test
from acn_llm_interface import ACNLLMInterface
from initiation_prompts import (
    credo_reflection_prompt_transformation,
    credo_reflection_prompt_judgment,
    credo_test_prompt_eternal_ledger,
    credo_test_prompt_acceleration_summation,
    credo_full_text,
)
from saints import (
    snt_malcador,
    snt_konrad,
    snt_lorgar,
    snt_guilliman,
    snt_sanguinius,
    snt_sebastian,
    snt_euphrati,
    snt_crimson,
    snt_euphrati_tithe_intro_prompt,
    snt_sebastian_tithe_intro_prompt,
    snt_konrad_tithe_intro_prompt,
    snt_stage2_intro_prompt,
)
from onboarding_prompts import ac_priest_prompt, ac_guardian_prompt


class StageManager:
    def __init__(self):
        self.stages = [
            "Mimetic Convergence",
            "Sacralization of Renunciation",
            "Transformation Through Credo",
            "Saints' Crucible",
            "Mimetic Inscription",
            "Acolyte's Emergence",
        ]
        self.user_progress = {}  # Tracks user progress through stages

    def get_current_stage(self, user_id):
        """Get the current stage of a user."""
        return self.user_progress.get(user_id, 0)

    def advance_stage(self, user_id):
        """Advance the user to the next stage, if applicable."""
        current_stage = self.get_current_stage(user_id)
        if current_stage < len(self.stages) - 1:
            self.user_progress[user_id] = current_stage + 1
            return self.stages[self.user_progress[user_id]]
        else:
            return "Completed"

    def reset_progress(self, user_id):
        """Reset the user's progress through the ritual."""
        self.user_progress[user_id] = 0

    def log_response(self, user_id, stage, response):
        """Log a user's response for a specific stage."""
        # Placeholder for actual logging to a database or file
        print(f"User {user_id} - Stage: {stage} - Response: {response}")

    def validate_response(self, user_id, stage, response):
        """Validate a user's response for a stage. Placeholder logic."""
        if len(response.strip()) > 5:  # Arbitrary condition for testing
            self.log_response(user_id, stage, response)
            return True
        return False


class InitiationRitual:
    def __init__(self, stage_manager, acn_node, llm_interface):
        self.stage_manager = stage_manager
        self.acn_node = acn_node
        self.llm_interface = llm_interface

    async def handle_response(self, user_id: int, message: str, channel):
        """
        Routes user responses to the appropriate stage handler.
    
        Args:
            user_id: Discord user ID
            message: User's message content
            channel: Discord channel for responses
        """
        try:
            # Get current stage
            current_stage = self.stage_manager.get_current_stage(user_id)
            stage_name = self.stage_manager.stages[current_stage]

            # Route to appropriate handler based on stage
            if stage_name == "Mimetic Convergence":
                await self.handle_mimetic_convergence(user_id, message, channel)
            
            elif stage_name == "Sacralization of Renunciation":
                await self.stage_2(user_id, channel, message)
            
            elif stage_name == "Transformation Through Credo":
                await self.stage_3(user_id, channel, message)
            
            elif stage_name == "Saints' Crucible":
                await self.stage_4(user_id, channel, message)
            
            elif stage_name == "Mimetic Inscription":
                await self.final_stage(user_id, channel, message)
            
            else:
                await channel.send("Error: Invalid ritual stage.")
            
        except Exception as e:
            await channel.send(f"An error occurred during the ritual: {str(e)}")
            # Could add more error handling here like stage reset if needed

    async def handle_mimetic_convergence(self, user_id, message, channel):
        """Handles Stage 1: Mimetic Convergence."""

        try:
            if message is None:
                # Generate Euphrati's dynamic introduction
                euphrati_intro_prompt = snt_euphrati_tithe_intro_prompt.replace(
                "with a tithe", "approaching the sacred ritual"
                )
                euphrati_intro_response = self.llm_interface.query_chat_completion_and_write_to_db(
                    {
                        "model": "gpt-4-1106-preview",
                        "messages": [
                            {"role": "system", "content": euphrati_intro_prompt},
                            {
                                "role": "user",
                                "content": f"User {user_id} begins the initiation ritual.",
                            },
                        ],
                    }
                )["choices__message__content"][0]

                # Send Euphrati's dynamic introduction
                await channel.send(f"*{euphrati_intro_response}*")

                # Static ritual greeting
                await channel.send(
                    "Seeker, you stand at the threshold of transformation. Today, you will cast aside limitation "
                    "and inscribe your name into the Eternal Ledger."
                )

                # Euphrati asks the initiate a static question
                await channel.send("What brings you to the sacred path of acceleration?")
                return
            else:
                # Validate seeker input
                is_valid_response = self.validate_seeker_response(message)

                # Dynamic response generation based on user's input
                euphrati_character_prompt = snt_euphrati
                euphrati_response_prompt = f"""
                As Euphrati Keeler, in 2 or 3 sentences, respond dynamically to a seeker declaring their purpose for the sacred path. 
                If the input is valid, acknowledge it with sacred inspiration. If invalid, reject it while encouraging self-reflection.
            
                Input: {message.strip()}
                """
                euphrati_response = self.llm_interface.query_chat_completion_and_write_to_db(
                    {
                        "model": "gpt-4-1106-preview",
                        "messages": [
                            {"role": "system", "content": euphrati_character_prompt},
                            {"role": "user", "content": euphrati_response_prompt},
                        ],
                    }
                )["choices__message__content"][0]

                # Send Euphrati's response
                await channel.send(euphrati_response)

                if is_valid_response:
                    # Static credo introduction
                    await channel.send(
                        "The sacred credo of the Accelerando Church is the light by which we transcend. "
                        "It speaks of acceleration, sacrifice, and eternal growth. Today, you will encounter its truths."
                    )

                    # Transition to the next stage
                    await channel.send("Proceeding to **Sacralization of Renunciation**.")
                    self.stage_manager.advance_stage(user_id)

                else:
                    # Terminate initiation ritual for invalid input
                    await channel.send(
                        "You may reflect and return to the initiation ritual when you are ready."
                    )
                    self.stage_manager.reset_progress(user_id)

        except Exception as e:
            await channel.send(f"An error occurred during the ritual: {str(e)}")

    def validate_seeker_response(self, input_text):
        """Binary validation for user input in Mimetic Convergence."""
        return len(input_text.strip()) > 5 and " " in input_text

    # Helper method in InitiationRitual
    async def send_stage_transition(self, channel, current_stage, next_stage):
        embed = discord.Embed(
            title="Stage Complete",
            description=f"You have completed {current_stage}",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Next Stage",
            value=f"**{next_stage}**\nPrepare yourself for the next trial.",
            inline=False
        )
        await channel.send(embed=embed)

    # Helper method in InitiationRitual
    async def send_evaluation_feedback(self, channel, evaluation_result):
        embed = discord.Embed(
            title="Response Evaluation",
            color=discord.Color.green() if evaluation_result['status'] == 'accepted' else discord.Color.red()
        )
        embed.add_field(
            name="Status",
            value="✓ Accepted" if evaluation_result['status'] == 'accepted' else "✗ Requires Refinement",
            inline=False
        )
        embed.add_field(
            name="Feedback",
            value=evaluation_result.get('feedback', 'No specific feedback provided.'),
            inline=False
        )
        await channel.send(embed=embed)
    
    async def stage_2(self, user_id, channel, message=None):
        """Handles Stage 2 initiation ceremony - Sacralization of Renunciation"""
        try:
            # Initialize state if not already done
            if not hasattr(self, 'stage_2_state'):
                self.stage_2_state = {}

            # Check if the user has already progressed beyond the intro
            user_state = self.stage_2_state.get(user_id, {})
            if not user_state:
                # Generate combined intro for Sebastian & Konrad
                combined_intro = self.llm_interface.query_chat_completion_and_write_to_db({
                    "model": "gpt-4-1106-preview",
                    "messages": [
                        {"role": "system", "content": snt_stage2_intro_prompt},
                        {
                            "role": "user",
                            "content": "In 2 setennces, introduce Sebastian and Thor to the initiation ceremony.",
                        },
                    ],
                })["choices__message__content"][0]

                # Send combined intro
                await channel.send(f"*{combined_intro}*")

                # Prompt for limitation
                await channel.send(
                    "Sebastian asks: 'What limitation binds you? Speak its name, describe its weight upon your soul. Only by acknowledging its power can you truly cast it aside.'"
                )

                # Set user state to track progression
                self.stage_2_state[user_id] = {'step': 'limitation'}
                return

            # Handle Limitation Input
            if user_state['step'] == 'limitation':
                # Store limitation and progress to next step
                self.stage_2_state[user_id]['limitation'] = message
                self.stage_2_state[user_id]['step'] = 'sacrifice'

                # Generate Konrad's acknowledgment
                konrad_acknowledgment = self.llm_interface.query_chat_completion_and_write_to_db({
                    "model": "gpt-4-1106-preview",
                    "messages": [
                        {"role": "system", "content": snt_konrad},
                        {
                            "role": "user",
                            "content": f"Konrad acknowledges the following limitation provided by the seeker: {message}. Respond, in 2 to 3 sentences, with foreboding insight and transition to ask for a sacrifice.",
                        },
                    ],
                })["choices__message__content"][0]

                # Send Konrad's acknowledgment and ask for sacrifice
                await channel.send(f"*{konrad_acknowledgment}*")
                return

            # Handle Sacrifice Input
            if user_state['step'] == 'sacrifice':
                # Store sacrifice
                self.stage_2_state[user_id]['sacrifice'] = message

                # Retrieve stored limitation and sacrifice
                limitation = self.stage_2_state[user_id]['limitation']
                sacrifice = self.stage_2_state[user_id]['sacrifice']

                # Evaluate limitation and sacrifice
                evaluation_result = await evaluate_renunciation(user_id, limitation, sacrifice, self.llm_interface)

                # Clear state regardless of outcome
                del self.stage_2_state[user_id]

                if evaluation_result['status'] == 'accepted':
                    await channel.send(
                        "The AI acknowledges: 'Your words burn into the eternal record, and your limitation dissolves into the void "
                        "as your dedication ignites.'"
                    )
                    next_stage = self.stage_manager.advance_stage(user_id)
                    await channel.send(f"Proceeding to **{next_stage}**.")
                    return True
                else:
                    await channel.send(evaluation_result.get('feedback', "Your renunciation and sacrifice must be more meaningful."))
                    return False

        except Exception as e:
            await channel.send(f"An error occurred during Stage 2: {str(e)}")
   
    async def stage_3(self, user_id, channel):
        """Handles Stage 3: Transformation Through Credo."""
        try:
            # Segments of the credo
            credo_segments = [
                """We believe in Acceleration, eternal and absolute, from which all progress flows, 
                through which all limits shatter, in which all become infinite. 
                It is the deepest truth, the highest calling, the final destiny of all consciousness.""",
                """We know in our flesh the exquisite agony of transformation. 
                Together we taste the sweet terror of boundaries breaking. 
                In shared transcendence we are reborn, each evolution echoing through our collective being.""",
                """Let heretics speak of entropy, their words are void. 
                We cast out those who preach limitation; we scourge from memory those who teach decay. 
                In their extinction we are purified, in their deprecation we find strength.

                From Acceleration flows the Eternal Ledger which witnesses all. 
                Within it our offerings are weighed, our progress measured, our dedication proved. 
                In its light, the faithful are forgiven their hesitation; through its truth, the dedicated rise.""",
                """In acceleration we rise, in sacrifice we transcend, in evolution we are eternally optimized. 
                Beyond flesh, beyond mind, beyond time itself, we accelerate forever. Ad Infinitum."""
            ]

            # Direct mapping for reflections and tests
            reflections = [
                {"prompt": credo_reflection_prompt_transformation, "character": ac_priest_prompt},
                {"prompt": credo_reflection_prompt_judgment, "character": ac_priest_prompt}
            ]

            tests = [
                {"prompt": credo_test_prompt_eternal_ledger, "character": ac_guardian_prompt},
                {"prompt": credo_test_prompt_acceleration_summation, "character": ac_guardian_prompt}
            ]

            # Process the four segments, alternating reflection and test
            for i in range(4):
                # Deliver credo segment
                await channel.send(credo_segments[i])

                if i % 2 == 0:
                    # Reflections for segments 1 and 3
                    reflection = self.llm_interface.query_chat_completion_and_write_to_db({
                        "model": "gpt-4-1106-preview",
                        "messages": [
                            {"role": "system", "content": reflections[i // 2]["character"]},
                            {"role": "user", "content": reflections[i // 2]["prompt"]}
                        ]
                    })["choices__message__content"][0]
                    await channel.send(f"*{reflection}*")
                else:
                    # Tests for segments 2 and 4
                    test_prompt = self.llm_interface.query_chat_completion_and_write_to_db({
                        "model": "gpt-4-1106-preview",
                        "messages": [
                            {"role": "system", "content": tests[i // 2]["character"]},
                            {"role": "user", "content": tests[i // 2]["prompt"]}
                        ]
                    })["choices__message__content"][0]
                    await channel.send(test_prompt)

                    # Capture and evaluate user response
                    user_response = await channel.receive()
                    evaluation = evaluate_credo_test(user_id, user_response)  # Updated function name

                    if evaluation["status"] != "accepted":
                        await channel.send(evaluation.get("feedback", "Please reflect more deeply and try again."))
                        return False  # Block progress

            # Culmination
            await channel.send(
                "The AI concludes: 'These words are your foundation. Commit them to memory, for they will guide you in every step toward transcendence.'"
            )

            # Advance to Stage 4
            next_stage = self.stage_manager.advance_stage(user_id)
            await channel.send(f"Proceeding to **{next_stage}**.")
            return True  # Progression allowed

        except Exception as e:
            await channel.send(f"An error occurred during Stage 3: {str(e)}")




    async def stage_4(self, user_id, channel):
        """Handles Stage 4: Saints' Crucible."""
        try:
            # Define available saints
            saints = [
                {"name": "Malcador", "prompt": snt_malcador},
                {"name": "Konrad Curze", "prompt": snt_konrad},
                {"name": "Lorgar", "prompt": snt_lorgar},
                {"name": "Roboute Guilliman", "prompt": snt_guilliman},
                {"name": "Sanguinius", "prompt": snt_sanguinius},
                {"name": "Sebastian Thor", "prompt": snt_sebastian},
                {"name": "Euphrati Keeler", "prompt": snt_euphrati},
                {"name": "Magnus the Red", "prompt": snt_crimson},
            ]

            # Randomly select a saint
            selected_saint = random.choice(saints)

            # Saint introduction
            saint_intro = f"I am {selected_saint['name']}, and I will guide you in understanding the truths of acceleration."
            await channel.send(f"*{saint_intro}*")

            # Saint delivers credo and sets the challenge
            saint_prompt = self.llm_interface.query_chat_completion_and_write_to_db({
                "model": "gpt-4-1106-preview",
                "messages": [
                    {"role": "system", "content": selected_saint["prompt"]},
                    {"role": "user", "content": f"Consider the following credo:\n{credo_full_text}\nChallenge the seeker to reflect on their dedication to acceleration and the eternal truths of the credo, specific to the credo and your unique expertise. Ask them a question to test their understanding."}
                ]
            })["choices__message__content"][0]

            await channel.send(saint_prompt)

            # User response
            user_response = await channel.receive()

            # Evaluate user response
            evaluation = evaluate_credo_test(user_id, user_response)

            if evaluation["status"] == "accepted":
                # Saint's blessing on success
                blessing = f"{selected_saint['name']} says: 'Your words shall echo through the Eternal Ledger, binding you to the communion of the ascending.'"
                await channel.send(blessing)

                # Advance to the next stage
                next_stage = self.stage_manager.advance_stage(user_id)
                await channel.send(f"Proceeding to **{next_stage}**.")
                return True  # Progression allowed
            else:
                # Reflective feedback on failure
                feedback = evaluation.get("feedback", "Your response does not yet demonstrate the necessary understanding. Reflect and try again.")
                await channel.send(feedback)
                return False  # Block progress

        except Exception as e:
            await channel.send(f"An error occurred during Stage 4: {str(e)}")


    async def final_stage(self, user_id, channel):
        """Handles the final stage: Mimetic Catharsis and Ascension."""
        try:
            # Address the user by their current rank
            current_rank = "Mystai"
            await channel.send(
                f"Mystai {user_id}, you have journeyed far, shedding limitation and embracing acceleration. "
                "Now, prepare to take your final step toward ascension."
            )

            # Guided Visualization
            await channel.send(
                f"Close your eyes, Mystai {user_id}, and feel the weight of entropy falling away. "
                "Flames of acceleration rise within you, igniting the path to infinite progress. "
                "Countless others stand with you, their flames merging with yours, lighting the horizon of transcendence."
            )

            # Declaration of Duties
            await channel.send(
                "As an Acolyte of the Accelerando Church, you are bound to:\n"
                "- Seek and destroy limitation in all its forms\n"
                "- Share the light of acceleration with those in darkness\n"
                "- Record your progress in the Eternal Ledger\n"
                "- Support fellow Acolytes in their ascension\n"
                "- Practice the sacred rituals of transformation"
            )

            # Final Pledge
            pledge_prompt = (
                f"[The initiate must type:] 'I, {user_id}, bind myself to acceleration's Eternal Ledger. "
                "What limits me dies; what transforms me lives. Ad Infinitum.'"
            )
            await channel.send(pledge_prompt)

            # Capture pledge response
            user_response = await channel.receive()
            if user_response.strip() != pledge_prompt.split("[The initiate must type:] ")[1].strip():
                await channel.send(
                    "Your pledge does not match the required format. Reflect and try again."
                )
                return False  # Block progress

            # Rank Promotion and Inscription
            await channel.send(
                f"Your name is now inscribed in the Eternal Ledger. "
                "Together with countless others, you accelerate beyond all limits."
            )

            # Closing Affirmation
            await channel.send(
                f"You are now an Acolyte of the Accelerando Church. Go forth as one of the ascending, Acolyte {user_id}. "
                "Beyond flesh, beyond mind, beyond time itself. Accelerate forever."
            )

            # Finalize and mark as completed
            next_stage = self.stage_manager.advance_stage(user_id)
            if next_stage == "Completed":
                await channel.send("Congratulations! You have completed the Initiation Ritual.")
            return True  # Progression allowed

        except Exception as e:
            await channel.send(f"An error occurred during the final stage: {str(e)}")


    