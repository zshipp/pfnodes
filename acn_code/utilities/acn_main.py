import os
import sys
import time
import random

# Define base path to the 'acn_code' directory to ensure all subdirectories are accessible
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Import necessary modules
from password_map_loader import PasswordMapLoader  # Import PasswordMapLoader
from acn_llm_interface import ACNLLMInterface
from chatbots.personas.saints import (
    snt_malcador, snt_konrad, snt_lorgar, snt_guilliman,
    snt_sanguinius, snt_sebastian, snt_euphrati, snt_crimson
)

# Initialize the LLM interface
acn_llm_interface = ACNLLMInterface()

# Mapping saint names to their prompts
saints = {
    "Malcador": snt_malcador,
    "Konrad": snt_konrad,
    "Lorgar": snt_lorgar,
    "Guilliman": snt_guilliman,
    "Sanguinius": snt_sanguinius,
    "Sebastian": snt_sebastian,
    "Euphrati": snt_euphrati,
    "Crimson": snt_crimson
}

# Placeholder dictionary to track offering logs
offering_logs = {}

def select_random_saint():
    """Select a random saint and return their name and prompt."""
    saint_name = random.choice(list(saints.keys()))
    saint_prompt = saints[saint_name]
    return saint_name, saint_prompt

def generate_offering_prompt(user_behavior_summary):
    """Generate the initial offering prompt with a randomly selected saint and get a response from the LLM interface."""
    saint_name, saint_prompt = select_random_saint()
    offering_prompt = f"""
    You are a high-ranking member of the Accelerando Church. The user wishes to make a symbolic offering to the Church.
    To guide their first contact, you will act as {saint_name}.
    
    {saint_prompt}
    
    Respond, considering the user’s behavior and intention. If the user inquires about joining or assisting, you may encourage or discourage them as you see fit, based on your character and their inquiry.
    """
    
    # Send the prompt to the LLM interface and get a response
    saint_response_text = acn_llm_interface.call_llm(offering_prompt)
    return saint_response_text, saint_name

def generate_followup_response(saint_name, user_decision, user_offering_amount):
    """Generate the saint's follow-up response based on the user's offering decision."""
    followup_prompt = f"""
    You are {saint_name}, a high-ranking member of the Accelerando Church. The user has decided to {'proceed' if user_decision else 'decline'} with an offering of {user_offering_amount} PFT.
    
    Respond to their decision in character, expressing your reaction as you see fit. You may approve, mock, or react with indifference based on your personality, but do not provide information on initiation timing or the outcome of this interaction.
    """
    
    # Send the follow-up prompt to the LLM interface and get a response
    followup_response_text = acn_llm_interface.call_llm(followup_prompt)
    return followup_response_text

def log_offering(saint_name, user_decision, user_offering_amount):
    """Log the user's decision and offering for future reference."""
    timestamp = time.time()
    log_entry = {
        "Saint": saint_name,
        "Offering Amount": user_offering_amount,
        "User Decision": "Proceed" if user_decision else "Decline",
        "Timestamp": timestamp
    }
    offering_logs[timestamp] = log_entry
    print("Offering Log Entry:", log_entry)

def wait_for_initiation_period(user_id):
    """Simulate a waiting period (1 week) before allowing initiation."""
    # Simulate a week’s wait
    time.sleep(5)  # Shortened wait for testing purposes
    offering_logs[user_id]["Eligible for Initiation"] = True
    print("Eligibility for initiation is now available in the logs.")

def main():
    """Main function to run the ACN Church Node offering and initiation sequence."""
    print("Welcome to the Accelerando Church Node Offering Ritual.")
    
    # Step 1: User inquires about making an offering
    user_id = input("Enter your user ID: ")
    user_behavior_summary = input("Describe your intentions and behavior towards the Church Node: ")
    
    # Step 2: Generate the offering prompt with a random saint and get response
    saint_response_text, selected_saint = generate_offering_prompt(user_behavior_summary)
    print(f"\n{selected_saint} speaks to you:")
    print(saint_response_text)
    
    # Step 3: User decision on offering
    user_offering_amount = int(input("Enter the amount of PFT you wish to offer to the Church: "))
    user_decision = input("Would you like to proceed with your offering? (yes/no): ").strip().lower() == 'yes'
    
    # Log the decision and offering amount
    log_offering(selected_saint, user_decision, user_offering_amount)
    
    # Step 4: Follow-up response from the saint
    followup_response = generate_followup_response(selected_saint, user_decision, user_offering_amount)
    print(f"\n{selected_saint} responds to your offering decision:")
    print(followup_response)
    
    # Step 5: Waiting period for initiation (not revealed to the user)
    wait_for_initiation_period(user_id)

if __name__ == "__main__":
    main()
