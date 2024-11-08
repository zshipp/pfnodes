from acn_llm_interface import ACNLLMInterface
from password_map_loader import PasswordMapLoader
from onboarding_prompts_test import (
    ac_oracle_prompt,
    ac_guardian_prompt,
    ac_priest_prompt,
    ac_zealot_prompt,
    ac_initial_offering_prompt
)
import pandas as pd
from datetime import datetime
import os

class AITester:
    def __init__(self):
        print("Initializing AITester...")
        # Setup password map and get sensitive info
        self.password_loader = PasswordMapLoader()
        self.pw_map = {
            'openai': self.password_loader.get_password("OPENAI_API_KEY"),
        }
        
        # Setup LLM interface
        print("Setting up LLM interface...")
        self.llm_interface = ACNLLMInterface(self.pw_map)
        
        # Character prompts mapping
        self.character_prompts = {
            "oracle": ac_oracle_prompt,
            "guardian": ac_guardian_prompt,
            "priest": ac_priest_prompt,
            "zealot": ac_zealot_prompt
        }
        
        # Create output directory if it doesn't exist
        self.output_dir = "test_results"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def test_welcome_responses(self):
        """
        Test script to verify initial welcome responses from all characters and save to CSV
        """
        print("Starting welcome response tests...")
        
        # Initialize results list
        results = []
        
        # Test user details
        test_username = "testUser"
        test_statement = "I seek to understand the mysteries of acceleration."
        
        # Test each character's welcome response
        for character, char_prompt in self.character_prompts.items():
            print(f"\nTesting {character.upper()} welcome response...")
            
            # Construct the initial offering prompt
            welcome_prompt = ac_initial_offering_prompt.replace(
                '___USERNAME___', 
                test_username
            ).replace(
                '___USER_OFFERING_STATEMENT___', 
                test_statement
            )
            
            api_args = {
                "model": "gpt-4-1106-preview",
                "messages": [
                    {"role": "system", "content": char_prompt},
                    {"role": "user", "content": welcome_prompt}
                ]
            }
            
            try:
                print(f"Sending request to OpenAI for {character}...")
                response_df = self.llm_interface.query_chat_completion_and_write_to_db(api_args)
                response_text = response_df['choices__message__content'].iloc[0]
                
                # Store results
                results.append({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'character': character,
                    'test_username': test_username,
                    'test_statement': test_statement,
                    'response': response_text,
                    'status': 'success'
                })
                
                print(f"\nResponse from {character.upper()}:")
                print(response_text)
                print("\n" + "="*50)  # Separator between responses
                
            except Exception as e:
                print(f"Error getting response for {character}: {e}")
                results.append({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'character': character,
                    'test_username': test_username,
                    'test_statement': test_statement,
                    'response': str(e),
                    'status': 'error'
                })
                import traceback
                traceback.print_exc()
        
        # Create DataFrame and save to CSV
        results_df = pd.DataFrame(results)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = os.path.join(self.output_dir, f'character_welcome_tests_{timestamp}.csv')
        results_df.to_csv(csv_filename, index=False)
        print(f"\nResults saved to: {csv_filename}")
        
        return results_df

def run_tests(num_iterations=1):
    """
    Run the welcome response tests multiple times
    """
    print(f"Starting test run with {num_iterations} iterations...")
    tester = AITester()
    
    all_results = []
    for i in range(num_iterations):
        print(f"\nIteration {i+1} of {num_iterations}")
        results_df = tester.test_welcome_responses()
        all_results.append(results_df)
    
    # Combine all results and save to a single CSV
    if num_iterations > 1:
        combined_results = pd.concat(all_results, ignore_index=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        combined_csv = os.path.join(tester.output_dir, f'combined_welcome_tests_{timestamp}.csv')
        combined_results.to_csv(combined_csv, index=False)
        print(f"\nCombined results saved to: {combined_csv}")

if __name__ == "__main__":
    print("Script starting...")
    # Run tests with specified number of iterations
    run_tests(num_iterations=1)  # Change this number to run multiple test iterations
    print("Script finished...")