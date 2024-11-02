import os
import logging
from openai import OpenAI
from password_map_loader import PasswordMapLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ACNLLMInterface:
    def __init__(self, llm_choice='openai', model='gpt-4'):
        self.llm_choice = llm_choice
        self.model = model
        self.api_key = PasswordMapLoader().get_password('OPENAI_API_KEY')
        
        # Initialize the OpenAI client
        self.client = OpenAI(api_key=self.api_key)

    def set_llm_api_key(self, api_key):
        """Allows setting API key manually, if needed."""
        self.client.api_key = api_key

    def call_llm(self, prompt):
        """Executes the LLM call with a given prompt and returns the response for ACN."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200  # Adjust token limit as necessary
            )
            # Accessing the response as an attribute instead of using dictionary-style indexing
            response_content = response.choices[0].message.content.strip()
            return response_content
        except Exception as e:
            logger.error(f"Error in LLM call: {str(e)}")
            return "Error: Unable to get a response from the LLM."
