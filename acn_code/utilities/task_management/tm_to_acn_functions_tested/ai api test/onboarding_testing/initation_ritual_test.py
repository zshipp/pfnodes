import asyncio
from initiation_ritual import InitiationRitual, StageManager
from saints import snt_euphrati_tithe_intro_prompt
from acn_llm_interface import ACNLLMInterface


# Mock LLM Interface
class MockLLMInterface:
    def query_chat_completion_and_write_to_db(self, api_args):
        content = api_args["messages"][1]["content"]
        if "Sebastian Thor" in api_args["messages"][0]["content"]:
            return {
                "choices__message__content": [
                    "Sebastian Thor stands with quiet yet transformative authority, his gaze filled with divine purpose."
                ]
            }
        elif "Konrad Curze" in api_args["messages"][0]["content"]:
            return {
                "choices__message__content": [
                    "Konrad Curze materializes from the shadows, his aura heavy with foreboding judgment."
                ]
            }
        elif "limitation" in content:
            return {
                "choices__message__content": [
                    f"Konrad acknowledges the limitation: '{content}'."
                ]
            }
        else:
            return {
                "choices__message__content": [
                    "Euphrati Keeler stands as a beacon of truth and faith, her presence turning the moment sacred."
                ]
            }


# Mock AI Judging
def mock_evaluate_renunciation(user_id, limitation, sacrifice):
    if len(limitation) > 5 and len(sacrifice) > 5:
        return {"status": "accepted"}
    else:
        return {"status": "rejected", "feedback": "Your responses lack sufficient depth. Please elaborate."}


# Test Harness
async def test_stage_2():
    stage_manager = StageManager()
    mock_llm = MockLLMInterface()
    ritual = InitiationRitual(stage_manager, None, mock_evaluate_renunciation, mock_llm)

    # Test cases
    test_cases = [
        {
            "user_id": "123",
            "limitation": "I renounce fear of failure.",
            "sacrifice": "I sacrifice the comfort of indecision.",
            "expected": "Proceeding to **Transformation Through Credo**.",
        },
        {
            "user_id": "456",
            "limitation": "Fear.",
            "sacrifice": "None.",
            "expected": "Your renunciation and sacrifice must be more meaningful.",
        },
    ]

    for test in test_cases:
        print(f"Testing user ID: {test['user_id']}")

        class MockChannel:
            async def send(self, content):
                print(f"Channel message: {content}")

            async def receive(self):
                if not hasattr(self, "received"):
                    self.received = test["limitation"]
                else:
                    self.received = test["sacrifice"]
                return self.received

        channel = MockChannel()
        success = await ritual.stage_2(test["user_id"], channel)

        # Check for expected output
        if success:
            print(f"Expected: {test['expected']}")

# Run Tests
if __name__ == "__main__":
    asyncio.run(test_stage_2())
