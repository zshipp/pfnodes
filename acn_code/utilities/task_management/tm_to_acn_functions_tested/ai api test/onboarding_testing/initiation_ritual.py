from ai_judging import AIJudgingTool, evaluate_renunciation
from acn_llm_interface import ACNLLMInterface
from saints import (
    snt_euphrati_tithe_intro_prompt,
    snt_euphrati,
    snt_sebastian_tithe_intro_prompt,
    snt_konrad_tithe_intro_prompt,
    snt_konrad,
)


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
    def __init__(self, stage_manager, acn_node, ai_judge, llm_interface):
        self.stage_manager = stage_manager
        self.acn_node = acn_node
        self.ai_judge = ai_judge
        self.llm_interface = llm_interface

    async def handle_mimetic_convergence(self, user_id, message, channel):
        """Handles Stage 1: Mimetic Convergence."""

        try:
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

            # Validate seeker input
            is_valid_response = self.validate_seeker_response(message)

            # Dynamic response generation based on user's input
            euphrati_character_prompt = snt_euphrati
            euphrati_response_prompt = f"""
            As Euphrati Keeler, respond dynamically to a seeker declaring their purpose for the sacred path. 
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

    async def stage_2(self, user_id, channel):
        # Handles Stage 2 initiation ceremony - Sacralization of Renunciation
        try:
            # Combined dynamic intro for Sebastian and Konrad
            sebastian_intro = self.llm_interface.query_chat_completion_and_write_to_db(
                {
                    "model": "gpt-4-1106-preview",
                    "messages": [
                        {"role": "system", "content": snt_sebastian_tithe_intro_prompt},
                        {
                            "role": "user",
                            "content": "Describe Sebastian Thor introducing Stage 2.",
                        },
                    ],
                }
            )["choices__message__content"][0]

            konrad_intro = self.llm_interface.query_chat_completion_and_write_to_db(
                {
                    "model": "gpt-4-1106-preview",
                    "messages": [
                        {"role": "system", "content": snt_konrad_tithe_intro_prompt},
                        {
                            "role": "user",
                            "content": "Describe Konrad Curze introducing Stage 2.",
                        },
                    ],
                }
            )["choices__message__content"][0]

            # Send dynamic intro to user
            await channel.send(f"*{sebastian_intro}*\n*{konrad_intro}*")

            # Sebastian's prompt for limitation
            sebastian_prompt = (
                "Sebastian asks: 'What limitation binds you? Speak its name, describe its weight upon your soul. "
                "Only by acknowledging its power can you truly cast it aside.'"
            )
            await channel.send(sebastian_prompt)
            limitation = await channel.receive()  # Replace with appropriate method for getting user input

            # Konrad dynamically acknowledges the limitation
            konrad_ack = self.llm_interface.query_chat_completion_and_write_to_db(
                {
                    "model": "gpt-4-1106-preview",
                    "messages": [
                        {"role": "system", "content": snt_konrad},
                        {
                            "role": "user",
                            "content": f"Respond dynamically to this limitation: '{limitation}'.",
                        },
                    ],
                }
            )["choices__message__content"][0]
            await channel.send(f"*{konrad_ack}*")

            # Konrad asks for sacrifice
            konrad_prompt = (
                "Konrad asks: 'What will you sacrifice to break this chain? What comfort will you abandon for acceleration?'"
            )
            await channel.send(konrad_prompt)
            sacrifice = await channel.receive()  # Replace with appropriate method for getting user input

            # Send responses to the AI judge for evaluation
            evaluation_result = evaluate_renunciation(user_id, limitation, sacrifice)

            # Handle AI judge feedback
            if evaluation_result['status'] == 'accepted':
                await channel.send(
                    "The AI acknowledges: 'Your words burn into the eternal record, and your limitation dissolves into the void "
                    "as your dedication ignites.'"
                )

                # Advance to Stage 3
                next_stage = self.stage_manager.advance_stage(user_id)
                await channel.send(f"Proceeding to **{next_stage}**.")
                return True  # Progression allowed
            else:
                feedback = evaluation_result.get(
                    "feedback", "Your renunciation and sacrifice must be more meaningful."
                )
                await channel.send(f"Feedback: {feedback}")
                return False  # Lock progression until refinement

        except Exception as e:
            await channel.send(f"An error occurred during Stage 2: {str(e)}")
