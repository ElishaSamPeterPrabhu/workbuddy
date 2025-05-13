from core.ai_client import AIClient

if __name__ == "__main__":
    ai_client = AIClient()  # Ensure your API key/env is set up!
    user_query = "check for check_colab12.txt "
    results = ai_client.get_response(user_query)
    print("Final results:", results)
