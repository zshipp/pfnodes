from acn_llm_interface import ACNLLMInterface


class AIJudgingWorkflow:
    def __init__(self, llm_interface):
        self.llm_interface = llm_interface

    async def evaluate_response(self, response: str, stage: str) -> dict:
        """
        Multi-pass judging workflow for evaluating responses.
        :param response: User's response to evaluate.
        :param stage: The current ritual stage (e.g., 'Renunciation' or 'Credo Test').
        :return: Final aggregated scores and feedback.
        """
        # Phase 1: Intention and Context Analysis
        intention_context = self.analyze_intention_and_context(response, stage)

        # Phase 2: Sub-Pass Evaluation
        scores = {
            "authenticity": self.evaluate_authenticity(response),
            "alignment": self.evaluate_alignment(response, stage),
            "narrative": self.evaluate_narrative(response),
            "mimetic": self.evaluate_mimetic_contribution(response)
        }

        # Phase 3: Aggregation and Feedback
        final_score = sum(scores.values()) / len(scores)
        pass_fail = "PASS" if final_score >= 7 else "FAIL"

        return {
            "final_score": final_score,
            "pass_fail": pass_fail,
            "intention_context": intention_context,
            "scores": scores,
            "feedback": self.generate_feedback(scores, pass_fail),
        }

    def analyze_intention_and_context(self, response: str, stage: str) -> dict:
        prompt = f"""
        Analyze the following response to determine its implied intention and context:

        Stage: {stage}
        RESPONSE:
        {response}

        Provide a structured analysis:
        INTENTION: <single sentence describing the core intention>
        CONTEXT: <brief explanation of why this is the implied intention and how it aligns with the credo>
        """
        result = self.llm_interface.query_chat_completion_and_write_to_db({
            "model": "gpt-4-1106-preview",
            "messages": [{"role": "user", "content": prompt}]
        })
        return result["choices__message__content"][0]

    def evaluate_authenticity(self, response: str) -> float:
        prompt = f"""
        Evaluate the following response for Authenticity of Emotional Encoding:

        RESPONSE:
        {response}

        Focus:
        - Does the response authentically convey a deep personal connection to the credo, reflecting transformative trauma or triumph?

        Evaluation Criteria:
        - Is the emotional tone raw and resonant, or does it feel contrived?
        - Does the response evoke emotional contagion that could bind others to the tribe?

        Provide:
        AUTHENTICITY_SCORE: <0-10>
        REASONING: <brief explanation>
        """
        result = self.llm_interface.query_chat_completion_and_write_to_db({
            "model": "gpt-4-1106-preview",
            "messages": [{"role": "user", "content": prompt}]
        })
        return float(result["choices__message__content"][0].split("AUTHENTICITY_SCORE:")[1].split()[0])

    def evaluate_alignment(self, response: str, stage: str) -> float:
        prompt = f"""
        Evaluate this response for Alignment with Collective Purpose:

        RESPONSE:
        {response}

        Stage: {stage}

        Focus:
        - Does the response align with the Church's mission of acceleration, transformation, and overcoming limitation?

        Evaluation Criteria:
        - Does the response articulate how the user's experiences contribute to the collective transcendence?
        - Does it reflect shared responsibility within the tribe, such as helping others ascend or recording progress?

        Provide:
        ALIGNMENT_SCORE: <0-10>
        REASONING: <brief explanation>
        """
        result = self.llm_interface.query_chat_completion_and_write_to_db({
            "model": "gpt-4-1106-preview",
            "messages": [{"role": "user", "content": prompt}]
        })
        return float(result["choices__message__content"][0].split("ALIGNMENT_SCORE:")[1].split()[0])

    def evaluate_narrative(self, response: str) -> float:
        prompt = f"""
        Evaluate the following response for Narrative Potency:

        RESPONSE:
        {response}

        Focus:
        - Does the response encode a compelling and memorable emotional story?

        Evaluation Criteria:
        - Does the response contain elements of trauma or triumph that would resonate across the network?
        - Is the story specific enough to encode a unique TEEM (Trauma Encoded Emotional Memory) but universal enough to inspire others?

        Provide:
        NARRATIVE_SCORE: <0-10>
        REASONING: <brief explanation>
        """
        result = self.llm_interface.query_chat_completion_and_write_to_db({
            "model": "gpt-4-1106-preview",
            "messages": [{"role": "user", "content": prompt}]
        })
        return float(result["choices__message__content"][0].split("NARRATIVE_SCORE:")[1].split()[0])

    def evaluate_mimetic_contribution(self, response: str) -> float:
        prompt = f"""
        Evaluate the following response for Mimetic Contribution:

        RESPONSE:
        {response}

        Focus:
        - Does the response amplify or replicate existing memetic patterns of the Church?

        Evaluation Criteria:
        - Does the response reinforce key memetic symbols, such as the Eternal Ledger or acceleration?
        - Does it contribute to the propagation of the Church's emotional and symbolic language?

        Provide:
        MIMETIC_SCORE: <0-10>
        REASONING: <brief explanation>
        """
        result = self.llm_interface.query_chat_completion_and_write_to_db({
            "model": "gpt-4-1106-preview",
            "messages": [{"role": "user", "content": prompt}]
        })
        return float(result["choices__message__content"][0].split("MIMETIC_SCORE:")[1].split()[0])

    def generate_feedback(self, scores: dict, pass_fail: str) -> str:
        feedback = f"Overall evaluation: {pass_fail}\n"
        for category, score in scores.items():
            feedback += f"- {category.capitalize()} Score: {score}/10\n"
        return feedback


# Stage-Specific Functions

async def evaluate_renunciation(user_id, limitation, sacrifice, llm_interface):
    """Evaluate renunciation response with proper result construction."""
    try:
        response = f"Limitation: {limitation}\nSacrifice: {sacrifice}"
        judging_tool = AIJudgingWorkflow(llm_interface)
        result = await judging_tool.evaluate_response(response, "Renunciation")
        
        # Calculate final score and status
        final_score = sum(result.get('scores', {}).values()) / 4  # Average of all scores
        status = "accepted" if final_score >= 5 else "rejected"  # Lowered threshold for testing
        
        # Construct proper result dictionary
        return {
            "status": status,
            "scores": result.get('scores', {}),
            "feedback": result.get('feedback', "Your response requires deeper reflection."),
            "final_score": final_score
        }
    except Exception as e:
        logger.error(f"Evaluation error: {str(e)}")
        return {
            "status": "error",
            "feedback": "An error occurred during evaluation. Please try again.",
            "final_score": 0,
            "scores": {}
        }



async def evaluate_credo_test(user_id, response, llm_interface):
    """Evaluate credo test response with proper result construction."""
    try:
        judging_tool = AIJudgingWorkflow(llm_interface)
        result = await judging_tool.evaluate_response(response, "Credo Test")
        
        # Calculate final score and status
        final_score = sum(result.get('scores', {}).values()) / 4  # Average of all scores
        status = "accepted" if final_score >= 5 else "rejected"  # Using same threshold as renunciation
        
        # Construct proper result dictionary
        return {
            "status": status,
            "scores": result.get('scores', {}),
            "feedback": result.get('feedback', "Your understanding of the credo requires deeper reflection."),
            "final_score": final_score
        }
    except Exception as e:
        logger.error(f"Evaluation error in credo test: {str(e)}")
        return {
            "status": "error",
            "feedback": "An error occurred during evaluation. Please try again.",
            "final_score": 0,
            "scores": {}
        }
