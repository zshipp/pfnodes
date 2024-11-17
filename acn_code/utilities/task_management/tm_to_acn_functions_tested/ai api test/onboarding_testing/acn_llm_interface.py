import datetime
import psycopg2
import os
import pandas as pd
import json
import asyncio
import nest_asyncio
import uuid
from password_map_loader import PasswordMapLoader
from openai import OpenAI, AsyncOpenAI
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Database connection setup
def connect_to_db():
    password_loader = PasswordMapLoader()
    db_user = password_loader.get_password("POSTGRES_USER")
    db_password = password_loader.get_password("POSTGRES_PASSWORD")

    try:
        connection = psycopg2.connect(
            database="acn_database",
            user=db_user,
            password=db_password,
            host="localhost",
            port="5432"
        )
        print("Connection to database successful.")
        return connection
    except Exception as e:
        print("Error connecting to database:", e)
        return None

class ACNLLMInterface:
    def __init__(self, pw_map):
        self.pw_map = pw_map
        self.client = OpenAI(api_key=self.pw_map['openai'])
        self.async_client = AsyncOpenAI(api_key=self.pw_map['openai'])
        
        # Get database credentials
        password_loader = PasswordMapLoader()
        db_user = password_loader.get_password("POSTGRES_USER")
        db_password = password_loader.get_password("POSTGRES_PASSWORD")
        
        self.db_engine = create_engine(f'postgresql://{db_user}:{db_password}@localhost/acn_database')
        print("ACN LLM Interface Initialized with GPT-4 model.")
    
    def generate_job_hash(self):
        """Generates a unique job hash for tracking purposes."""
        return str(uuid.uuid4())

    def run_chat_completion_sync(self, api_args):
        """Run synchronous chat completion with given API arguments."""
        output = self.client.chat.completions.create(**api_args)
        return output

    def run_chat_completion_async_demo(self):
        """Demo run for asynchronous chat completion with predefined examples."""
        job_hashes = [f'job{i}sample__{self.generate_job_hash()}' for i in range(1, 6)]
        arg_async_map = {
            job_hashes[0]: {
                "model": "gpt-4-1106-preview",
                "messages": [
                    {"role": "system", "content": "world's most smooth liar"},
                    {"role": "user", "content": "explain an elaborate excuse for being late"}
                ]
            },
            job_hashes[1]: {
                "model": "gpt-4-1106-preview",
                "messages": [
                    {"role": "system", "content": "crafty and sneaky liar"},
                    {"role": "user", "content": "explain elaborate excuse for lateness"}
                ]
            },
            job_hashes[2]: {
                "model": "gpt-4-1106-preview",
                "messages": [
                    {"role": "system", "content": "persuasive person"},
                    {"role": "user", "content": "convince spouse why adultery is a good idea"}
                ]
            },
        }
        async_write_df = self.create_writable_df_for_async_chat_completion(arg_async_map=arg_async_map)
        return async_write_df

    async def get_completions(self, arg_async_map):
        """Asynchronously get completions for a set of arguments."""
        async def task_with_debug(job_name, api_args):
            print(f"Task {job_name} start: {datetime.datetime.now().time()}")
            response = await self.async_client.chat.completions.create(**api_args)
            print(f"Task {job_name} end: {datetime.datetime.now().time()}")
            return job_name, response

        tasks = [asyncio.create_task(task_with_debug(job_name, args)) 
                for job_name, args in arg_async_map.items()]
        return await asyncio.gather(*tasks)

    def create_writable_df_for_chat_completion(self, api_args):
        """Create a DataFrame from chat completion response"""
        completion_object = self.run_chat_completion_sync(api_args)
        raw_df = pd.DataFrame(completion_object.model_dump(), index=[0]).copy()
        
        # Debug print to see what we're getting
        print("Choices content:", raw_df['choices'].iloc[0])
        
        # Safer access to choices
        def safe_extract(x):
            try:
                return x['finish_reason'] if isinstance(x, dict) else x[0]['finish_reason']
            except (KeyError, IndexError, TypeError):
                return None

        raw_df['choices__finish_reason'] = raw_df['choices'].apply(safe_extract)
        raw_df['choices__index'] = raw_df['choices'].apply(lambda x: x.get('index') if isinstance(x, dict) else x[0].get('index'))
        raw_df['choices__message__content'] = raw_df['choices'].apply(lambda x: x['message'].get('content') if isinstance(x, dict) else x[0]['message'].get('content'))
        raw_df['choices__message__role'] = raw_df['choices'].apply(lambda x: x['message'].get('role') if isinstance(x, dict) else x[0]['message'].get('role'))
        raw_df['choices__message__function_call'] = raw_df['choices'].apply(lambda x: x['message'].get('function_call') if isinstance(x, dict) else x[0]['message'].get('function_call'))
        raw_df['choices__message__tool_calls'] = raw_df['choices'].apply(lambda x: x['message'].get('tool_calls') if isinstance(x, dict) else x[0]['message'].get('tool_calls'))
        raw_df['choices__log_probs'] = raw_df['choices'].apply(lambda x: x.get('logprobs') if isinstance(x, dict) else x[0].get('logprobs'))
        raw_df['choices__json'] = raw_df['choices'].apply(json.dumps)
        raw_df['write_time'] = datetime.datetime.now()
        return raw_df

    def create_writable_df_for_async_chat_completion(self, arg_async_map):
        """Create DataFrame for async chat completion results"""
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        x1 = loop.run_until_complete(self.get_completions(arg_async_map=arg_async_map))
        dfarr = []
        for xobj in x1:
            internal_name = xobj[0]
            completion_object = xobj[1]
            raw_df = pd.DataFrame(completion_object.model_dump(), index=[0]).copy()
            
            # Debug print
            print("Async Choices content:", raw_df['choices'].iloc[0])
            
            # Extract the fields we want
            choices = raw_df['choices'].iloc[0]  # It's already a dict
            raw_df['choices__finish_reason'] = choices.get('finish_reason')
            raw_df['choices__index'] = choices.get('index')
            raw_df['choices__message__content'] = choices['message'].get('content')
            raw_df['choices__message__role'] = choices['message'].get('role')
            raw_df['choices__message__function_call'] = choices['message'].get('function_call')
            raw_df['choices__message__tool_calls'] = choices['message'].get('tool_calls')
            raw_df['choices__log_probs'] = choices.get('logprobs')
            raw_df['write_time'] = datetime.datetime.now()
            raw_df['internal_name'] = internal_name

            # Convert dict columns to JSON strings for PostgreSQL compatibility
            for col in raw_df.columns:
                if isinstance(raw_df[col].iloc[0], (dict, list)):
                    raw_df[col] = raw_df[col].apply(json.dumps)

            dfarr.append(raw_df)
        
        full_writable_df = pd.concat(dfarr)
        return full_writable_df

    def query_chat_completion_async_and_write_to_db(self, arg_async_map):
        """Query chat completion asynchronously and write result to database"""
        async_write_df = self.create_writable_df_for_async_chat_completion(arg_async_map=arg_async_map)
        try:
            # Drop both choices and internal_name columns
            if 'choices' in async_write_df.columns:
                async_write_df = async_write_df.drop('choices', axis=1)
            if 'internal_name' in async_write_df.columns:
                async_write_df = async_write_df.drop('internal_name', axis=1)
            self._write_df_to_db(async_write_df, 'acn_chat_completions')
            return async_write_df
        except Exception as e:
            print(f"Error writing to database: {e}")
            return async_write_df

    def query_chat_completion_and_write_to_db(self, api_args):
        """Query chat completion and write the result to database"""
        writable_df = self.create_writable_df_for_chat_completion(api_args=api_args)
        try:
            # Drop the original choices column as we've extracted what we need
            if 'choices' in writable_df.columns:
                writable_df = writable_df.drop('choices', axis=1)
            self._write_df_to_db(writable_df, 'acn_chat_completions')
            return writable_df
        except Exception as e:
            print(f"Error writing to database: {e}")
            return writable_df

    def _write_df_to_db(self, dataframe, table_name):
        """Helper method to write DataFrame to a PostgreSQL table."""
        try:
            dataframe.to_sql(table_name, self.db_engine, if_exists='append', index=False)
            print(f"Data successfully written to {table_name} table.")
        except SQLAlchemyError as e:
            print(f"Error writing data to {table_name} table: {e}")

    def output_all_openai_chat_completions(self):
        """Fetches and outputs all chat completions stored in the database."""
        query = "SELECT * FROM acn_chat_completions"
        with self.db_engine.connect() as connection:
            all_completions = pd.read_sql(query, connection)
        return all_completions

    def run_sample_logs_test(self):
        """Run a quick test of logging functionality with sample completions"""
        print("Starting sample logs test...")
        
        # Test 1: Synchronous completion
        sync_args = {
            "model": "gpt-4-1106-preview",
            "messages": [
                {"role": "user", "content": "Write a brief greeting"}
            ]
        }
        
        # Run sync test
        print("Testing synchronous completion logging...")
        sync_result = self.query_chat_completion_and_write_to_db(sync_args)
        print(f"Sync completion logged with ID: {sync_result['id'].iloc[0]}")
        
        # Test 2: Async completions batch
        async_args = {
            f'test_job_{i}_{self.generate_job_hash()}': {
                "model": "gpt-4-1106-preview",
                "messages": [
                    {"role": "user", "content": f"Quick test message {i}"}
                ]
            } for i in range(3)  # Testing with 3 async completions
        }
        
        print("\nTesting async completion logging...")
        async_results = self.query_chat_completion_async_and_write_to_db(async_args)
        
        # Verify logs
        print("\nVerifying logged completions...")
        all_logs = self.output_all_openai_chat_completions()
        print(f"Total completions logged: {len(all_logs)}")
        print("Recent completion timestamps:")
        print(all_logs['write_time'].tail())
        
        return all_logs

if __name__ == "__main__":
    # Database connection testing
    db_connection = connect_to_db()
    if db_connection:
        # Initialize password loader
        password_loader = PasswordMapLoader()
        pw_map = {
            'openai': password_loader.get_password("OPENAI_API_KEY"),
            # Add other necessary passwords from your password map
        }
        
        # Create interface and run test
        llm_interface = ACNLLMInterface(pw_map)
        test_results = llm_interface.run_sample_logs_test()
        
        db_connection.close()