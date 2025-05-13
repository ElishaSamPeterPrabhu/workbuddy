"""
Test script for the AI client in WorkBuddy (Jarvis Assistant).

TODO: Migrate all tests to /tests/ with pytest and proper structure.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ai_client import AIClient, WorkflowState, Document


def main():
    print("=== WorkBuddy AI Test ===")
    print("Type 'exit' to quit")
    print()

    # Initialize AI client
    ai_client = AIClient()

    # Print API configuration
    print(f"API URL: {ai_client.base_url}")
    print(f"Assistant ID: {ai_client.assistant_id}")
    print(f"API Token available: {'Yes' if ai_client.access_token else 'No'}")
    print()

    # Load system prompt if it exists
    if os.path.exists("system_prompt.txt"):
        with open("system_prompt.txt", "r") as f:
            system_prompt = f.read()
            # Override the system prompt in the AI client
            try:
                ai_client.system_prompt = system_prompt
                print("Loaded custom system prompt from system_prompt.txt")
            except:
                print("Note: AI client does not support system_prompt attribute")

    # Main interaction loop
    while True:
        # Get user input
        user_input = input("You: ")

        # Check for exit command
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Exiting. Goodbye!")
            break

        # Get response from AI
        try:
            # First try with verbose debugging
            print("Calling API...")
            state = WorkflowState(
                user_query=user_input, retrieved_docs=[Document(page_content="")]
            )
            result = ai_client.rag_qa(state)
            print(f"API Result: {result}")

            response = ai_client.get_response(user_input)
            print(f"WorkBuddy: {response}")
            print()
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
