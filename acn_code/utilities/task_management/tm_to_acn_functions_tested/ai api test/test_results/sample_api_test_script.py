from acn_llm_interface import ACNLLMInterface
from password_map_loader import PasswordMapLoader
from onboarding_prompts_test import (
    ac_oracle_prompt,
    ac_guardian_prompt,
    ac_priest_prompt,
    ac_zealot_prompt,
    ac_initial_offering_prompt,
    ac_no_offering_prompt,
    ac_standard_offering_prompt,
    ac_significant_offering_prompt,
    ac_exceptional_offering_prompt,
    ac_insane_offering_prompt
)
import random
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
        
        # Offering prompts mapping
        self.offering_prompts = {
            "NO_OFFERING": ac_no_offering_prompt,
            "STANDARD_OFFERING": ac_standard_offering_prompt,
            "SIGNIFICANT_OFFERING": ac_significant_offering_prompt,
            "EXCEPTIONAL_OFFERING": ac_exceptional_offering_prompt,
            "INSANE_OFFERING": ac_insane_offering_prompt
        }
        
        # Create output directory if it doesn't exist
        self.output_dir = "test_results"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def test_character_responses(self):
        """
        Test script to verify AI responses from different characters
        """
        print("Starting character tests...")
        
        # Initialize results list
        results = []
        
        # Test user details
        test_username = "testUser"
        test_statement = "I seek to understand the mysteries of acceleration."
        
        # Test offering responses
        print("\nTesting offering responses...")
        test_offerings = {
            "NO_OFFERING": "0",
            "STANDARD_OFFERING": "100",
            "SIGNIFICANT_OFFERING": "2000",
            "EXCEPTIONAL_OFFERING": "10000",
            "INSANE_OFFERING": "20000"
        }
        
        for offering_type, amount in test_offerings.items():
            print(f"\nTesting {offering_type} response...")
            
            # Randomly select character but store which one we picked
            selected_char = random.choice(["oracle", "guardian", "priest", "zealot"])
            char_prompt = self.character_prompts[selected_char]
            
            print(f"Using {selected_char.upper()} character...")
            
            api_args = {
                "model": "gpt-4-1106-preview",
                "messages": [
                    {"role": "system", "content": char_prompt},
                    {"role": "user", "content": self.offering_prompts[offering_type].replace('___USERNAME___', test_username).replace('___USER_OFFERING_STATEMENT___', amount)}
                ]
            }
            
            try:
                print(f"Sending request to OpenAI for {offering_type} with {selected_char}...")
                response_df = self.llm_interface.query_chat_completion_and_write_to_db(api_args)
                response_text = response_df['choices__message__content'].iloc[0]
                
                # Store results
                results.append({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'offering_type': offering_type,
                    'offering_amount': amount,
                    'character': selected_char,
                    'test_username': test_username,
                    'response': response_text,
                    'status': 'success'
                })
                
                print(f"\nResponse from {selected_char.upper()}:")
                print(response_text)
                
            except Exception as e:
                print(f"Error getting response: {e}")
                results.append({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'offering_type': offering_type,
                    'offering_amount': amount,
                    'character': selected_char,
                    'test_username': test_username,
                    'response': str(e),
                    'status': 'error'
                })
                import traceback
                traceback.print_exc()
        
        # Create DataFrame and save to CSV
        results_df = pd.DataFrame(results)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = os.path.join(self.output_dir, f'offering_tests_{timestamp}.csv')
        results_df.to_csv(csv_filename, index=False)
        print(f"\nResults saved to: {csv_filename}")
        
        return results_df

def run_tests(num_iterations=1):
    """
    Run the offering response tests multiple times
    """
    print(f"Starting test run with {num_iterations} iterations...")
    tester = AITester()
    
    all_results = []
    for i in range(num_iterations):
        print(f"\nIteration {i+1} of {num_iterations}")
        results_df = tester.test_character_responses()
        all_results.append(results_df)
    
    # Combine all results and save to a single CSV
    if num_iterations > 1:
        combined_results = pd.concat(all_results, ignore_index=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        combined_csv = os.path.join(tester.output_dir, f'combined_offering_tests_{timestamp}.csv')
        combined_results.to_csv(combined_csv, index=False)
        print(f"\nCombined results saved to: {combined_csv}")

if __name__ == "__main__":
    print("Script starting...")
    run_tests(num_iterations=1)  # Change this number to run multiple test iterations
    print("Script finished...")