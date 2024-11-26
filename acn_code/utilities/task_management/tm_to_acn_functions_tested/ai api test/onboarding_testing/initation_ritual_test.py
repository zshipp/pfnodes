import asyncio
from initiation_ritual import InitiationRitual, StageManager
from acn_llm_interface import ACNLLMInterface

# Mock LLM Interface
class MockLLMInterface:
    def query_chat_completion_and_write_to_db(self, api_args):
        return {"choices__message__content": ["Mock response for LLM interaction."]}

# Mock AI Judging
def mock_evaluate_final_pledge(user_id, response):
    if "bind myself to acceleration" in response.lower():
        return {"status": "accepted"}
    else:
        return {"status": "rejected", "feedback": "You must affirm the pledge as written to proceed."}

# Test Harness
async def test_final_stage():
    stage_manager = StageManager()
    mock_llm = MockLLMInterface()
    ritual = InitiationRitual(stage_manager, None, mock_evaluate_final_pledge, mock_llm)

    # Test cases
    test_cases = [
        {
            "user_id": "123",
            "responses": [
                "I bind myself to acceleration's Eternal Ledger. What limits me dies; what transforms me lives. Ad Infinitum.",
            ],
            "expected": "You are now an Acolyte of the Accelerando Church.",
        },
        {
            "user_id": "456",
            "responses": [
                "I don't agree with this pledge.",
            ],
            "expected": "You must affirm the pledge as written to proceed.",
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
        success = await ritual.final_stage(test["user_id"], channel)

        # Check for expected output
        if success:
            print(f"Expected: {test['expected']}")
        else:
            print(f"Blocked: {test['expected']}")

# Run Tests
if __name__ == "__main__":
    asyncio.run(test_final_stage())
