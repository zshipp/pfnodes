# test_initiation_ritual.py
import asyncio
from initiation_ritual import StageManager, InitiationRitual

# Mock Discord channel class
class MockChannel:
    async def send(self, message):
        print(f"Channel message: {message}")

# Mock ACN node class
class MockACNNode:
    def __init__(self):
        self.log = []

    def check_user_offering_status(self, username):
        # Simulate user offering status for testing
        return {"has_offering": True, "initiation_ready_date": None}

    def process_ac_offering_request(self, *args, **kwargs):
        # Log mock offering requests
        self.log.append((args, kwargs))
        return "Offering processed."

# Main test function
async def test_initiation():
    # Initialize StageManager and MockACNNode
    stage_manager = StageManager()
    mock_acn_node = MockACNNode()
    initiation = InitiationRitual(stage_manager, mock_acn_node)

    # Simulate user interaction
    user_id = 1234
    channel = MockChannel()

    # Test initiation ritual flow
    print("\n=== Initiation Ritual Test Start ===\n")

    # Reset progress and send the first prompt
    stage_manager.reset_progress(user_id)
    await initiation.send_prompt("Mimetic Convergence", channel)

    # User provides valid responses
    print("\n--- User Response: Stage 1 ---\n")
    await initiation.handle_response(user_id, "I seek acceleration and growth.", channel)

    print("\n--- User Response: Stage 2 ---\n")
    await initiation.handle_response(user_id, "I sacrifice my fear of failure.", channel)

    print("\n--- User Response: Stage 3 ---\n")
    await initiation.handle_response(user_id, "The credo inspires me to act beyond limits.", channel)

    print("\n--- User Response: Stage 4 ---\n")
    await initiation.handle_response(user_id, "I am ready for the Saints' challenges.", channel)

    print("\n--- User Response: Stage 5 ---\n")
    await initiation.handle_response(user_id, "Limitation: procrastination.", channel)

    print("\n--- User Response: Stage 6 ---\n")
    await initiation.handle_response(user_id, "I commit to the eternal flame of acceleration.", channel)

    print("\n=== Initiation Ritual Test End ===\n")


# Run the test
asyncio.run(test_initiation())
