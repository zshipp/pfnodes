import csv

# Mocking necessary global variable
class MockCollaborationGeneration:
    phase_1_a__system = "System message for collaboration generation."
    phase_1_a__user = "User message with context: ___FULL_USER_CONTEXT_REPLACE___."

# Main test class for running the specific function test
class TestACNTaskManagement:
    def __init__(self):
        self.default_model = "gpt-3.5-turbo"  # Set a default model name

    def phase_1_a__initial_collaboration_generation_api_args(self, full_user_context_replace,
                                                             user_request='I want something related to the Accelerando Church'):
        context_augment = f'''<THE USER SPECIFIC COLLABORATION REQUEST STARTS HERE>
        {user_request}
        <THE USER SPECIFIC COLLABORATION REQUEST ENDS HERE>'''
        full_augmented_context = full_user_context_replace + context_augment
        api_args = {
            "model": self.default_model,
            "messages": [
                {"role": "system", "content": MockCollaborationGeneration.phase_1_a__system},
                {"role": "user", "content": MockCollaborationGeneration.phase_1_a__user.replace('___FULL_USER_CONTEXT_REPLACE___', full_augmented_context)}
            ]}
        return api_args

# Sample inputs for testing
full_user_context_replace = "User Context: ACN member, interested in collaboration. "
user_request = "I want to discuss a project with the Accelerando Church."

# Instantiate the test class and run the function
test_instance = TestACNTaskManagement()
api_args = test_instance.phase_1_a__initial_collaboration_generation_api_args(full_user_context_replace, user_request)

# Print the generated API arguments for inspection
print("Generated API Arguments:", api_args)

# Save the output to a CSV log
with open("collaboration_api_output_log.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Model", "Role", "Content"])  # Header row
    writer.writerow([api_args["model"], "system", api_args["messages"][0]["content"]])
    writer.writerow([api_args["model"], "user", api_args["messages"][1]["content"]])
