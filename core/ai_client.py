"""
AI client module for WorkBuddy (Jarvis Assistant).

Handles communication with the AI backend for prompt-response interactions.

---
SYSTEM PROMPT FOR AI:
When the user asks about GitHub notifications, pull requests, repositories, or activity, always respond with a JSON block like:
```json
{ "action": "github_notifications", "ai_response": "Here are your latest GitHub notifications." }
```
or
```json
{ "action": "github_prs", "ai_response": "Here are your open GitHub pull requests." }
```
or
```json
{ "action": "github_repos", "ai_response": "Here are your repositories." }
```
or
```json
{ "action": "github_activity", "ai_response": "Here is your recent GitHub activity." }
```
Do NOT use "convo" for these requests. Only use "convo" for general conversation or non-GitHub topics.
---
"""

from typing import Optional, Any, Dict
import requests
import json
import os
import re
from core import storage  # <-- Add this import
from datetime import datetime, timezone
from core import scheduler
import dateutil.parser
import difflib
import logging
from integrations.github import GitHubIntegration
import fnmatch
from pathlib import Path
import time


class WorkflowState:
    """
    Helper class to structure data for the AI API call.
    """

    def __init__(
        self,
        user_query: str,
        retrieved_docs: Optional[list["Document"]] = None,
        file_details: Optional[dict] = None,
    ) -> None:
        """
        Initialize WorkflowState.

        Args:
            user_query: The user's query string.
            retrieved_docs: Optional list of Document objects.
            file_details: Optional dictionary of file details.
        """
        self.user_query = user_query
        self.retrieved_docs = retrieved_docs or [Document()]
        self.file_details = file_details


class Document:
    """
    Simple document class for retrieved docs.
    """

    def __init__(self, page_content: str = "") -> None:
        """
        Initialize Document.

        Args:
            page_content: The content of the document page.
        """
        self.page_content = page_content


class AIClient:
    """
    AI client for communicating with the backend API and generating responses.
    """

    def __init__(self, model_name: str = "gpt-4o-mini") -> None:
        """
        Initialize the AI client.

        Args:
            model_name: The model name to use for the API.
        """
        self.model_name = model_name

        # Trimble API setup
        self.assistant_id = "work-buddy"
        self.base_url = f"https://agw.construction-integration.trimble.cloud/trimbledeveloperprogram/assistants/v1/agents/{self.assistant_id}/messages"
        # self.access_token = os.environ.get(
        #     "TRIMBLE_API_TOKEN",
        #     "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2lkLnRyaW1ibGUuY29tIiwiZXhwIjoxNzQ1MzM3MTcwLCJuYmYiOjE3NDUzMzM1NzAsImlhdCI6MTc0NTMzMzU3MCwianRpIjoiYzdhM2ZmMDkxMmRiNGI0MmEzMWE1MDVjZTNkZmMyNzgiLCJqd3RfdmVyIjoyLCJzdWIiOiIwYzhkOGUwZC02MDU4LTQ2MGItYjExYS0xYTExMjE4NmFkNjQiLCJhcHBsaWNhdGlvbl9uYW1lIjoicmVsZWFzZS1ub3RlcyIsImlkZW50aXR5X3R5cGUiOiJhcHBsaWNhdGlvbiIsImF1dGhfdGltZSI6MTc0NTMzMzU3MCwiYW1yIjpbImNsaWVudF9jcmVkZW50aWFscyJdLCJhdWQiOlsiMGM4ZDhlMGQtNjA1OC00NjBiLWIxMWEtMWExMTIxODZhZDY0Il0sInNjb3BlIjoicmVsZWFzZS1ub3RlcyJ9.nrMAYOvxhZC6FLK_qHlJAWgWyx6flmPzaRFdbOwMl1qsW4he-eJetSpk7F3YL4_crjVYDpXtiJcKqNb2j-p5Qd-bHz8SOsyk_5h_T1gGq7xJw697CuCnB0HG_7ARVyb9lxL56BWegOoC3cot2UmZlXPSbiowJ92lbDQ0JcUpoAlAWJSr6rx7OsblZjAsr3hmDIMv1iDGjO4OZwkoZZSw_XuMowgTbckGsCnpnyO8PlsxYTTYTE1OqTCoJIRCK_pkEcdc6jh3O-lTKS8NELIjocLaXNJbzyKm_01ifpMZNNmuXO6CwTm7cW4sGIE18q1s2wiD8JO8qYHDFVwf0AgBGA",
        # )
        self.access_token="eyJhbGciOiJSUzI1NiIsImtpZCI6IjEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2lkLnRyaW1ibGUuY29tIiwiZXhwIjoxNzQ1MzM3MTcwLCJuYmYiOjE3NDUzMzM1NzAsImlhdCI6MTc0NTMzMzU3MCwianRpIjoiYzdhM2ZmMDkxMmRiNGI0MmEzMWE1MDVjZTNkZmMyNzgiLCJqd3RfdmVyIjoyLCJzdWIiOiIwYzhkOGUwZC02MDU4LTQ2MGItYjExYS0xYTExMjE4NmFkNjQiLCJhcHBsaWNhdGlvbl9uYW1lIjoicmVsZWFzZS1ub3RlcyIsImlkZW50aXR5X3R5cGUiOiJhcHBsaWNhdGlvbiIsImF1dGhfdGltZSI6MTc0NTMzMzU3MCwiYW1yIjpbImNsaWVudF9jcmVkZW50aWFscyJdLCJhdWQiOlsiMGM4ZDhlMGQtNjA1OC00NjBiLWIxMWEtMWExMTIxODZhZDY0Il0sInNjb3BlIjoicmVsZWFzZS1ub3RlcyJ9.nrMAYOvxhZC6FLK_qHlJAWgWyx6flmPzaRFdbOwMl1qsW4he-eJetSpk7F3YL4_crjVYDpXtiJcKqNb2j-p5Qd-bHz8SOsyk_5h_T1gGq7xJw697CuCnB0HG_7ARVyb9lxL56BWegOoC3cot2UmZlXPSbiowJ92lbDQ0JcUpoAlAWJSr6rx7OsblZjAsr3hmDIMv1iDGjO4OZwkoZZSw_XuMowgTbckGsCnpnyO8PlsxYTTYTE1OqTCoJIRCK_pkEcdc6jh3O-lTKS8NELIjocLaXNJbzyKm_01ifpMZNNmuXO6CwTm7cW4sGIE18q1s2wiD8JO8qYHDFVwf0AgBGA"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        # For session tracking
        self.session_id = "session_id1"
        self.interlocutor_id = "interlocutor_id"

        # Get user path information
        self.user_home = str(Path.home())
        self.username = os.path.basename(self.user_home)
        
        # Common user directories
        self.user_dirs = {
            "home": self.user_home,
            "desktop": os.path.join(self.user_home, "Desktop"),
            "documents": os.path.join(self.user_home, "Documents"),
            "downloads": os.path.join(self.user_home, "Downloads"),
            "pictures": os.path.join(self.user_home, "Pictures"),
            "videos": os.path.join(self.user_home, "Videos"),
            "music": os.path.join(self.user_home, "Music"),
        }

        # Add system prompt with instructions for file search phases and user paths
        self.file_search_prompt = f"""


IMPORTANT USER DIRECTORY INFORMATION - Use these exact paths for file operations:
- Home Directory: {self.user_home}
- Desktop: {self.user_dirs['desktop']}
- Documents: {self.user_dirs['documents']}
- Downloads: {self.user_dirs['downloads']}
- Pictures: {self.user_dirs['pictures']}
- Videos: {self.user_dirs['videos']}
- Music: {self.user_dirs['music']}

When the user asks you to find files, ALWAYS use the exact directory paths listed above. Do NOT use generic paths.
For example:
- Use "{self.user_dirs['desktop']}" instead of "Desktop" 
- Use "{self.user_dirs['documents']}" instead of "Documents"
- Use "{self.user_dirs['downloads']}" instead of "Downloads"

FILE SEARCH GUIDELINES:
1. For files with specific names, search directly with the pattern: "filename.ext"
2. For partial name matches, use wildcards: "*keyword*.ext"
3. For file extensions, always include the appropriate pattern: "*.pdf", "*.docx", etc.
4. When unsure about location, start with the most likely directory (Documents for documents, Downloads for downloaded files, etc.)
5. Always include the most specific directory path possible to speed up the search

When searching for files, you will use a phased approach:
1. First, a quick search is performed in high-priority locations (timeout: 15 seconds)
2. If files are found, you'll show the results
3. If the quick search times out, you'll need to decide based on the user's message whether to:
   a) Continue with a more extensive search (which takes longer but searches more locations)
   b) Ask for more specific information to narrow the search
   c) Try searching in a different location

For file search operations, respond with JSON in this format:
```json
{{
  "action": "convo",
  "is_reminder": false,
  "ai_response": "I'll search for that file for you.",
  "file_search": {{
    "action": "search_files_recursive",
    "directory": "{self.user_dirs['documents']}",
    "pattern": "example*.txt"
  }}
}}
```

When the user asks about previous search results or file locations, use the context provided to give details about where files were found.

When the user wants to continue a search, include a "continue_search" field in your JSON response:
```json
{{
  "action": "convo",
  "is_reminder": false,
  "ai_response": "I'll continue searching in more locations.",
  "file_search": {{
    "action": "search_files_recursive",
    "directory": "{self.user_home}",
    "pattern": "example*.txt",
    "continue_search": true
  }}
}}
```
"""

        # Simple fallback responses when no API connection is available
        self.fallback_responses: dict[str, str] = {
            "hello": "Hello! How can I help you today?",
            "hi": "Hi there! What can I do for you?",
            "how are you": "I'm functioning well, thank you! How can I assist you?",
            "help": "I can help you with various tasks like opening files, searching for information, or answering questions.",
            "bye": "Goodbye! Have a great day!",
            "thank you": "You're welcome! Is there anything else you need?",
            "thanks": "You're welcome! Is there anything else you need?",
            "who are you": "I'm WorkBuddy, your AI assistant for workplace productivity.",
            "what can you do": "I can help with opening applications, searching for information, answering questions, and more.",
        }

        # GitHub integration setup
        self.github_integration = GitHubIntegration()

        # New attributes for timeout and retries
        self.request_timeout = 15  # Reduced from 30 to 15 seconds for faster feedback
        self.max_retries = 2

        # User context for more helpful responses
        self.last_search_context_str = ""
        self.logger = logging.getLogger(__name__)

    def get_current_iso_time(self) -> str:
        """Return the current time in ISO 8601 format with timezone."""
        return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    def rag_qa(self, state: WorkflowState) -> dict[str, Any]:
        """
        Implementation of the Trimble API rag_qa logic.

        Args:
            state: The workflow state containing the user query and context.

        Returns:
            A dictionary with file details and the AI's answer.
        """
        try:
            # Prepare the message
            current_time = self.get_current_iso_time()
            message = f"{state.user_query}\n\ncurrent_time: {current_time}"
            body = {
                "message": message,
                "session_id": self.session_id,
                "interlocutor_id": self.interlocutor_id,
                "stream": False,
                "model_id": self.model_name,
            }

            # Make the API request
            response = requests.post(
                self.base_url, headers=self.headers, data=json.dumps(body)
            )

            # Parse the response
            answer = ""
            if response.status_code == 200:
                answer = response.json()["message"]
            print(response.json())
            return {
                "file_details": state.file_details or {},
                "rag_answer": answer,
            }
        except Exception as e:
            print(f"Error in rag_qa: {str(e)}")
            return {"file_details": {}, "rag_answer": f"Error: {str(e)}"}

    def get_response(self, user_message: str) -> str:
        """
        Get a response from the AI model based on the user's message.

        Args:
            user_message: The user's message string.

        Returns:
            The AI's response string.
        """
        try:
            print(f"DEBUG: Getting AI response for: {user_message}")
            
            # Check for reminder data in the message
            if "Here are the reminders:" in user_message:
                print("DEBUG: [AIClient] Detected reminder data in request")
                # Extract the JSON data to log it clearly
                try:
                    import json
                    import re
                    reminder_json_match = re.search(r'\{.*\}', user_message, re.DOTALL)
                    if reminder_json_match:
                        reminder_json = reminder_json_match.group(0)
                        parsed_json = json.loads(reminder_json)
                        print(f"DEBUG: [AIClient] Extracted reminder data: {json.dumps(parsed_json, indent=2)}")
                except Exception as e:
                    print(f"DEBUG: [AIClient] Error parsing reminder data: {e}")
            
            # If this is a simple demo, return a mock response
            if os.environ.get("MOCK_AI", "false").lower() == "true":
                print("DEBUG: [AIClient] Using mock AI mode")
                mock_response = self._get_mock_response(user_message)
                print(f"DEBUG: [AIClient] Mock response: {mock_response}")
                return mock_response
            
            # Otherwise call the API
            start_time = time.time()
            response = self._call_api(user_message)
            elapsed_time = time.time() - start_time
            
            # Log the full response for debugging purposes
            print(f"DEBUG: AI response received in {elapsed_time:.2f}s")
            
            # Check if response is JSON and log relevant parts for debugging
            try:
                import json
                parsed = json.loads(response)
                if "action" in parsed:
                    print(f"DEBUG: [AIClient] Response action: {parsed['action']}")
                    if parsed["action"] == "edit" and "reminder_id" in parsed:
                        print(f"DEBUG: [AIClient] Edit action detected for reminder_id={parsed['reminder_id']}")
                        print(f"DEBUG: [AIClient] Full edit details: {json.dumps(parsed, indent=2)}")
            except:
                # Not JSON or error parsing
                pass
                
            return response
            
        except Exception as e:
            import traceback
            self.logger.error(f"Error getting AI response: {e}")
            self.logger.error(traceback.format_exc())
            return f"Sorry, I encountered an error: {str(e)}"

    def _call_api(self, user_message: str, retry_count: int = 0) -> str:
        """
        Call the AI API with the user message.
        
        Args:
            user_message: User's message text
            retry_count: Current retry attempt (for internal use)
            
        Returns:
            AI's response text
        """
        try:
            # Check if we have the necessary API key
            if not self.access_token:
                return json.dumps({
                    "ai_response": "Error: API key not configured. Please set the TRIMBLE_API_TOKEN environment variable."
                })
            
            # Build context with search results if available
            context = ""
            if hasattr(self, 'last_search_context_str') and self.last_search_context_str:
                context = f"Context from previous searches: {self.last_search_context_str}\n\n"
            
            # Include file search prompt with the system instructions to ensure proper path usage
            system_instructions = self.file_search_prompt
            
            # Use the correct Trimble API format
            current_time = self.get_current_iso_time()
            message = f"{system_instructions}\n\n{context}{user_message}\n\ncurrent_time: {current_time}"
            
            payload = {
                "message": message,
                "session_id": self.session_id,
                "interlocutor_id": self.interlocutor_id,
                "stream": False,
                "model_id": self.model_name
            }
            
            # Make the API call with timeout
            response = requests.post(
                self.base_url, 
                headers=self.headers, 
                json=payload,
                timeout=self.request_timeout
            )
            
            # Check for successful response
            if response.status_code == 200:
                response_data = response.json()
                if "message" in response_data:
                    return response_data["message"]
                else:
                    return json.dumps({
                        "ai_response": "Received response from AI service but couldn't find expected content."
                    })
            else:
                # Handle API errors
                error_msg = f"API error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                
                # Fall back to mock response if API fails
                return self._get_mock_response(user_message)
                
        except requests.Timeout:
            error_msg = f"Request timed out after {self.request_timeout} seconds"
            self.logger.error(error_msg)
            return json.dumps({
                "ai_response": f"The AI service is taking too long to respond. Please try again or simplify your question."
            })
            
        except requests.RequestException as e:
            self.logger.error(f"Request exception: {e}")
            return self._get_mock_response(user_message)
            
        except Exception as e:
            self.logger.error(f"Unexpected error in API call: {e}")
            return self._get_mock_response(user_message)

    def _get_mock_response(self, user_message: str) -> str:
        """
        Generate a mock response for testing without calling an actual API.
        
        Args:
            user_message: User's message text
            
        Returns:
            Mocked AI response
        """
        # Simulate a brief delay
        time.sleep(0.5)
        
        # Simple command detection for file search demos
        if "find" in user_message.lower() or "search" in user_message.lower() or "file" in user_message.lower():
            search_term = user_message.split()[-1] if user_message.split() else ""
            
            # Use proper user paths
            return json.dumps({
                "action": "convo",
                "is_reminder": False,
                "ai_response": f"I'll search for files containing '{search_term}' in your Documents folder.",
                "file_search": {
                    "action": "search_files_recursive",
                    "pattern": f"*{search_term}*",
                    "directory": self.user_dirs["documents"]  # Use actual Documents path
                }
            })
        
        # Default response
        return json.dumps({
            "action": "convo",
            "is_reminder": False,
            "ai_response": f"This is a mock response to: {user_message}"
        })

    def get_fallback_response(self, user_message: str) -> str:
        """
        Generate a simple fallback response based on the user's message.

        Args:
            user_message: The user's message string.

        Returns:
            A fallback response string.
        """
        user_message = user_message.lower()

        # Check for exact matches in fallback responses
        for key, response in self.fallback_responses.items():
            if key in user_message:
                return response

        # Handle basic file operations
        if "open" in user_message and (
            "file" in user_message
            or "folder" in user_message
            or "directory" in user_message
        ):
            return "I'd be happy to help you open that, but I need to be properly configured first."

        # Handle search requests
        if (
            "search" in user_message
            or "find" in user_message
            or "look for" in user_message
        ):
            return "I can help you search for that once I'm properly set up with API access."

        # GitHub integration commands
        if "github notifications" in user_message:
            notifications = self.github_integration.get_notifications()
            if isinstance(notifications, list):
                if not notifications:
                    return "You have no new GitHub notifications."
                return "Your GitHub notifications:\n" + "\n".join(
                    f"- [{n['repository']}] {n['subject']} ({n['type']})"
                    for n in notifications
                )
            return notifications.get("error", "Error fetching notifications.")
        if "github prs" in user_message or "github pull requests" in user_message:
            prs = self.github_integration.get_pull_requests()
            if isinstance(prs, list):
                if not prs:
                    return "You have no open GitHub pull requests."
                return "Your open GitHub PRs:\n" + "\n".join(
                    f"- [{pr['repo']}] {pr['title']} (#{pr['number']})" for pr in prs
                )
            return prs.get("error", "Error fetching pull requests.")
        if "github summary" in user_message:
            return self.github_integration.generate_summary()

        # Default response
        return "I understand you want to know about that. Once I'm properly configured with API access, I'll be able to provide specific information."

    def handle_system_command(self, command: str) -> Optional[str]:
        """
        Handle system-specific commands.

        Args:
            command: The user's command string.

        Returns:
            A string response if a system command is recognized, otherwise None.
        """
        command = command.lower().strip()

        # Open applications
        if re.match(r"open (.*)", command):
            app_name = re.match(r"open (.*)", command).group(1).strip()
            return f"I'll try to open {app_name} for you once I have system access capabilities."

        # Search web
        if re.match(r"search (for )?(.*)", command) or "google" in command:
            query = re.sub(r"search (for )?|google", "", command).strip()
            return f"I'll search for '{query}' once I have web access capabilities."

        # No system command recognized
        return None

    def get_file_search_command(self, context: dict) -> dict:
        """
        Send the file search context to the AI and return the next command as a dict.

        Args:
            context: Dictionary with keys 'user_query', 'last_results', 'history', 'round'.

        Returns:
            dict: The AI's next file search command, e.g.:
                { "action": "file_search", "pattern": "*.py", "directory": "src" }
                or
                { "action": "stop", "ai_response": "File search complete." }
        """
        import re
        import json

        # Format candidate directories for the prompt
        candidate_dirs = context.get("candidate_directories", [])
        candidate_dirs_str = "\n".join(f"- {d}" for d in candidate_dirs)

        prompt = (
            getattr(self, "file_search_prompt", "")
            + "\n\n"
            + f"User query: {context['user_query']}\n"
            + f"Last results: {context['last_results']}\n"
            + f"History: {context['history']}\n"
            + f"Round: {context['round']}\n"
            + "Candidate directories (use ONLY these for the 'directory' field):\n"
            + candidate_dirs_str
            + "\nOnly use a directory from the above list for your next file search command.\n"
            + "What is the next file search command? Respond ONLY with a JSON object."
        )
        response = self.call_ai_model(prompt)
        if isinstance(response, dict) and "message" in response:
            response_text = response["message"]
        else:
            response_text = str(response)

        # Try to extract JSON from code block or anywhere in the string
        json_match = re.search(
            r"```json(.*?)```", response_text, re.DOTALL | re.IGNORECASE
        )
        if not json_match:
            json_match = re.search(r"```(.*?)```", response_text, re.DOTALL)
        if not json_match:
            json_match = re.search(r"\{.*?\}", response_text, re.DOTALL)

        if not json_match:
            # No JSON found, skip parsing and return stop with the message
            return {"action": "stop", "ai_response": response_text.strip()}

        json_str = (
            json_match.group(1).strip()
            if json_match.lastindex
            else json_match.group(0).strip()
        )

        # Try parsing the JSON, repairing backslashes if needed
        for attempt, repair in enumerate(
            [
                lambda s: s,  # original
                lambda s: s.replace("\\", "\\\\"),  # double all backslashes
                lambda s: re.sub(r"(?<!\\)\\(?![\\/])", r"\\\\", s),  # single to double
                lambda s: s.replace("\\", "/").replace(
                    "\\", "/"
                ),  # all to forward slash
            ]
        ):
            try:
                candidate = repair(json_str)
                print(f"[DEBUG] JSON parse attempt {attempt+1}: {candidate}")
                return json.loads(candidate)
            except Exception as e:
                print(f"[DEBUG] JSON parsing error (attempt {attempt+1}): {e}")

        print(f"[DEBUG] All JSON parsing attempts failed. Raw string: {json_str}")
        # If all else fails, treat as stop
        return {"action": "stop", "ai_response": response_text.strip()}

    def call_ai_model(self, prompt: str) -> str:
        """
        Use the direct method to prevent recursion.
        """
        return self.call_ai_model_direct(prompt)

    def call_ai_model_direct(self, prompt: str) -> str:
        """
        Direct call to the AI model without recursively calling get_response.
        """
        try:
            # Include system instructions for proper path usage
            system_instructions = self.file_search_prompt
            
            # Prepare the message for direct API call
            current_time = self.get_current_iso_time()
            body = {
                "message": f"{system_instructions}\n\n{prompt}",
                "session_id": self.session_id,
                "interlocutor_id": self.interlocutor_id,
                "stream": False,
                "model_id": self.model_name,
            }

            # Make the API request
            response = requests.post(
                self.base_url, headers=self.headers, data=json.dumps(body)
            )

            # Parse the response
            if response.status_code == 200:
                result = response.json().get("message", "")
                return result
            else:
                print(f"API Error: {response.status_code}")
                return ""
        except Exception as e:
            print(f"Error in direct AI model call: {str(e)}")
            return ""
