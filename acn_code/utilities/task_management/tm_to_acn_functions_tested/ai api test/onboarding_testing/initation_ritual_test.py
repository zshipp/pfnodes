import asyncio
from initiation_ritual import InitiationRitual, StageManager
from acn_llm_interface import ACNLLMInterface


# Mock LLM Interface
class MockLLMInterface:
    def query_chat_completion_and_write_to_db(self, api_args):
        content = api_args["messages"][1]["content"]
        if "Priest" in api_args["messages"][0]["content"]:
            return {
                "choices__message__content": [
                    "The Priest speaks enigmatically, guiding the seeker toward reflection."
                ]
            }
        elif "Guardian" in api_args["messages"][0]["content"]:
            return {
                "choices__message__content": [
                    "The Guardian's stern voice challenges the seeker to prove their worth."
                ]
            }
        else:
            return {
                "choices__message__content": [
                    "This is a test response for the given content."
                ]
            }


# Mock AI Judging
def mock_evaluate_credo_test(user_id, response):
    if len(response) > 10:  # Arbitrary threshold for valid responses
        return {"status": "accepted"}
    else:
        return {"status": "rejected", "feedback": "Your response lacks sufficient depth. Please elaborate."}


# Test Harness
async def test_stage_3():
    stage_manager = StageManager()
    mock_llm = MockLLMInterface()
    ritual = InitiationRitual(stage_manager, None, mock_evaluate_credo_test, mock_llm)

    # Test cases
    test_cases = [
        {
            "user_id": "123",
            "responses": [
                "I believe transformation is painful yet necessary.",
                "The Eternal Ledger inspires me to offer my dedication.",
                "Acceleration is my ultimate path.",
            ],
            "expected": "Proceeding to **Saints' Crucible**.",
        },
        {
            "user_id": "456",
            "responses": [
                "Short.",
                "Insufficient.",
                "Limited.",
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
        success = await ritual.stage_3(test["user_id"], channel)

        # Check for expected output
        if success:
            print(f"Expected: {test['expected']}")
        else:
            print(f"Blocked: {test['expected']}")

# Run Tests
if __name__ == "__main__":
    asyncio.run(test_stage_3())
