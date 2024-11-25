from acn_llm_interface import ACNLLMInterface

class AIJudgingTool:
    def __init__(self, llm_interface):
        """
        Initialize the AI Judging Tool with the specified LLM interface.
        :param llm_interface: Instance of ACNLLMInterface.
        """
        self.llm_interface = llm_interface

    async def evaluate_response(self, stage, response):
        """
        Evaluate a response for emotional authenticity and commitment.
        :param stage: The current ritual stage (str).
        :param response: The user's response to evaluate (str).
        :return: A dictionary containing evaluation scores and reasoning.
        """
        prompt = {
            "model": "gpt-4-1106-preview",
            "messages": [{
                "role": "user",
                "content": f"""Evaluate the following response for emotional authenticity and commitment:
                
                Stage: {stage}
                Response: {response}
                
                Provide an evaluation in this format:
                AUTHENTICITY_SCORE: <0-10 score>
                COMMITMENT_SCORE: <0-10 score>
                REASONING: <brief explanation>"""
            }]
        }

        try:
            result_df = self.llm_interface.query_chat_completion_and_write_to_db(prompt)
            response_text = result_df["choices__message__content"].iloc[0]

            # Extract scores and reasoning from the response
            authenticity_score = float(re.search(r"AUTHENTICITY_SCORE:\s*(\d+\.?\d*)", response_text).group(1))
            commitment_score = float(re.search(r"COMMITMENT_SCORE:\s*(\d+\.?\d*)", response_text).group(1))
            reasoning = re.search(r"REASONING:\s*(.+)", response_text).group(1)

            return {
                "authenticity_score": authenticity_score,
                "commitment_score": commitment_score,
                "reasoning": reasoning
            }
        except Exception as e:
            print(f"Error evaluating response: {str(e)}")
            return {
                "authenticity_score": 0,
                "commitment_score": 0,
                "reasoning": "Evaluation failed"
            }

def evaluate_renunciation(user_id, limitation, sacrifice):
    # Placeholder AI logic for evaluating responses
    # Replace with actual AI API calls when integrated
    responses = {
        "limitation": limitation,
        "sacrifice": sacrifice
    }
    # Dummy response for now
    evaluation = {
        "status": "accepted" if len(limitation) > 10 and len(sacrifice) > 10 else "rejected",
        "feedback": "Your responses lack sufficient depth. Please elaborate."
    }
    return evaluation

def evaluate_credo_test(user_id, response):
    """Evaluate the user's response for credo test."""
    if len(response.strip()) > 10:  # Replace with real evaluation logic if needed
        return {"status": "accepted"}
    return {"status": "rejected", "feedback": "Your response lacks sufficient depth. Please elaborate."}


