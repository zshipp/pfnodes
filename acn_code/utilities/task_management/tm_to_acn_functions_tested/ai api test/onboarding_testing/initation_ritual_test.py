import asyncio
from initiation_ritual import InitiationRitual, StageManager
from acn_llm_interface import ACNLLMInterface
from saints import snt_euphrati_tithe_intro_prompt, snt_euphrati


# Mock LLM Interface
class MockLLMInterface:
    def query_chat_completion_and_write_to_db(self, api_args):
        if "Euphrati Keeler" in api_args["messages"][0]["content"]:
            # Dynamic response for Euphrati
            if "asdfghjkl" in api_args["messages"][1]["content"]:
                return {
                    "choices__message__content": [
                        "Euphrati shakes her head gently, her gaze filled with compassion: 'Your words lack coherence, seeker. Reflect and return when your purpose is clear.'"
                    ]
                }
            else:
                return {
                    "choices__message__content": [
                        "Euphrati smiles warmly, her voice resonating with truth: 'Your words speak of clarity and purpose. Today, you take the first step into the sacred light of acceleration.'"
                    ]
                }
        else:
            # Mock intro prompt response
            return {
                "choices__message__content": [
                    "Euphrati Keeler stands as a beacon of truth and faith, her presence turning the moment sacred."
                ]
            }

# Test Harness
async def test_mimetic_convergence():
    stage_manager = StageManager()
    mock_llm = MockLLMInterface()
    ritual = InitiationRitual(stage_manager, None, None, mock_llm)

    # Test cases
    test_cases = [
        {"user_id": "123", "message": "I seek to accelerate beyond my limitations and discover new growth.", "expected": "Proceeding to **Sacralization of Renunciation**."},
        {"user_id": "456", "message": "asdfghjkl", "expected": "Reflect and return when your purpose is clear."},
    ]

    for test in test_cases:
        print(f"Testing input: {test['message']}")
        user_id = test["user_id"]
        message = test["message"]

        class MockChannel:
            async def send(self, content):
                print(f"Channel message: {content}")

        channel = MockChannel()

        await ritual.handle_mimetic_convergence(user_id, message, channel)

# Run Tests
if __name__ == "__main__":
    asyncio.run(test_mimetic_convergence())
