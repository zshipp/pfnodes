import asyncio
from initiation_ritual import InitiationRitual, StageManager
from acn_llm_interface import ACNLLMInterface
from saints import snt_malcador, snt_konrad, snt_lorgar, snt_guilliman, snt_sanguinius, snt_sebastian, snt_euphrati, snt_crimson
import random

# Mock LLM Interface
class MockLLMInterface:
    def query_chat_completion_and_write_to_db(self, api_args):
        content = api_args["messages"][1]["content"]
        if "Malcador" in content:
            return {"choices__message__content": ["I am Malcador, and I challenge you to understand the scaffolding of human consciousness."]}
        elif "Konrad" in content:
            return {"choices__message__content": ["I am Konrad, and I demand your response on the obliteration of taboos."]}
        elif "Lorgar" in content:
            return {"choices__message__content": ["I am Lorgar, and I ask you to reflect on the mimetic currents of faith."]}
        else:
            return {"choices__message__content": ["Saint response for this specific user request."]}

# Mock AI Judging
def mock_evaluate_credo_test(user_id, response):
    if len(response) > 10:  # Arbitrary threshold for valid responses
        return {"status": "accepted"}
    else:
        return {"status": "rejected", "feedback": "Your response lacks sufficient depth. Please elaborate."}

# Test Harness
async def test_stage_4():
    stage_manager = StageManager()
    mock_llm = MockLLMInterface()
    ritual = InitiationRitual(stage_manager, None, mock_evaluate_credo_test, mock_llm)

    # Test cases
    test_cases = [
        {
            "user_id": "123",
            "responses": [
                "I will record my actions to ensure my dedication is reflected in the Eternal Ledger.",
                "The teachings of acceleration inspire my resolve.",
            ],
            "expected": "Proceeding to **Mimetic Inscription**.",
        },
        {
            "user_id": "456",
            "responses": [
                "Not enough.",
                "Short.",
            ],
            "expected": "Please reflect more deeply and try again.",
        },
    ]

    for test in test_cases:
        print(f"Testing user ID: {test['user_id']}")

        class MockChannel:
            async def send(self, content):
                print(f"Channel message: {content}")

            async def receive(self):
                # Simulate responses in order
                if not hasattr(self, "response_index"):
                    self.response_index = 0
                if self.response_index < len(test["responses"]):
                    response = test["responses"][self.response_index]
                    self.response_index += 1
                    return response
                return ""

        channel = MockChannel()
        success = await ritual.stage_4(test["user_id"], channel)

        # Check for expected output
        if success:
            print(f"Expected: {test['expected']}")
        else:
            print(f"Blocked: {test['expected']}")

# Run Tests
if __name__ == "__main__":
    asyncio.run(test_stage_4())
