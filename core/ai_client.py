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
        self.access_token = os.environ.get(
            "TRIMBLE_API_TOKEN",
            "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2lkLnRyaW1ibGUuY29tIiwiZXhwIjoxNzQ1MzM3MTcwLCJuYmYiOjE3NDUzMzM1NzAsImlhdCI6MTc0NTMzMzU3MCwianRpIjoiYzdhM2ZmMDkxMmRiNGI0MmEzMWE1MDVjZTNkZmMyNzgiLCJqd3RfdmVyIjoyLCJzdWIiOiIwYzhkOGUwZC02MDU4LTQ2MGItYjExYS0xYTExMjE4NmFkNjQiLCJhcHBsaWNhdGlvbl9uYW1lIjoicmVsZWFzZS1ub3RlcyIsImlkZW50aXR5X3R5cGUiOiJhcHBsaWNhdGlvbiIsImF1dGhfdGltZSI6MTc0NTMzMzU3MCwiYW1yIjpbImNsaWVudF9jcmVkZW50aWFscyJdLCJhdWQiOlsiMGM4ZDhlMGQtNjA1OC00NjBiLWIxMWEtMWExMTIxODZhZDY0Il0sInNjb3BlIjoicmVsZWFzZS1ub3RlcyJ9.nrMAYOvxhZC6FLK_qHlJAWgWyx6flmPzaRFdbOwMl1qsW4he-eJetSpk7F3YL4_crjVYDpXtiJcKqNb2j-p5Qd-bHz8SOsyk_5h_T1gGq7xJw697CuCnB0HG_7ARVyb9lxL56BWegOoC3cot2UmZlXPSbiowJ92lbDQ0JcUpoAlAWJSr6rx7OsblZjAsr3hmDIMv1iDGjO4OZwkoZZSw_XuMowgTbckGsCnpnyO8PlsxYTTYTE1OqTCoJIRCK_pkEcdc6jh3O-lTKS8NELIjocLaXNJbzyKm_01ifpMZNNmuXO6CwTm7cW4sGIE18q1s2wiD8JO8qYHDFVwf0AgBGA",
        )
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        # For session tracking
        self.session_id = "session_id1"
        self.interlocutor_id = "interlocutor_id"

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
        print(f"DEBUG: AIClient.get_response received: '{user_message}'")
        """
        Get a response from the AI model or generate a fallback response.

        Args:
            user_message: The user's message string.

        Returns:
            The AI's response as a string.
        """
        # Check if we need to handle a system command
        system_response = self.handle_system_command(user_message)
        if system_response:
            return system_response

        try:
            # Create a state object for the rag_qa function
            state = WorkflowState(
                user_query=user_message, retrieved_docs=[Document(page_content="")]
            )

            # Get response from the AI
            result = self.rag_qa(state)

            if result and result.get("rag_answer"):
                raw_answer = result["rag_answer"]
                # Extract JSON block from markdown-style code block
                match = re.search(r"```json\s*(\{.*?\})\s*```", raw_answer, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    try:
                        response_json = json.loads(json_str)
                        # Strictly handle only single-object action-based workflow
                        # Handle request_data action
                        if response_json.get("action") == "request_data":
                            data_type = response_json.get("data_type")
                            data = None
                            if data_type == "reminders":
                                data = storage.get_all_reminders_with_status()
                            elif data_type == "notes":
                                data = storage.get_notes()
                            elif data_type == "notifications":
                                data = storage.get_notifications()
                            else:
                                return f"Unknown data_type requested: {data_type}"
                            # Compose a new prompt for the AI with the data
                            new_prompt = (
                                f"Here is the requested data as JSON. Use this data to answer the user's previous request.\n"
                                f'```json\n{{"data_type": "{data_type}", "data": {json.dumps(data, default=str)} }}\n```'
                            )
                            # Call get_response so the full action logic is processed
                            return self.get_response(new_prompt)
                        # Handle view action
                        elif response_json.get("action") == "view":
                            reminders = storage.get_all_reminders_with_status()
                            if reminders:
                                reminders_list = []
                                for i, r in enumerate(reminders):
                                    # Format time nicely
                                    try:
                                        dt = datetime.datetime.fromisoformat(
                                            r["remind_at"]
                                        )
                                        time_str = dt.strftime("%b %d, %Y, %I:%M %p")
                                    except Exception:
                                        time_str = r["remind_at"]
                                    reminders_list.append(
                                        f"{i+1}. {r['message']}\n    Time: {time_str}\n    Status: {r['status']}"
                                    )
                                ai_message = (
                                    "Here are your reminders:\n\n"
                                    + "\n\n".join(reminders_list)
                                )
                            else:
                                ai_message = "You have no reminders."
                            return ai_message
                        # Handle edit action
                        elif response_json.get("action") == "edit":
                            reminder_id = response_json.get("reminder_id")
                            new_message = response_json.get("new_message")
                            new_remind_at = response_json.get("new_remind_at")
                            old_message = response_json.get("old_message") or None

                            print(
                                f"DEBUG: edit action received: reminder_id={reminder_id}, new_message={new_message}, new_remind_at={new_remind_at}"
                            )

                            if not reminder_id:
                                # Always trigger request_data for edit if no id
                                all_reminders = storage.get_all_reminders_with_status()
                                return (
                                    "To proceed with editing, here is all reminder data. Please reply with an 'edit' action and the correct reminder_id.\n"
                                    f'```json\n{{"action": "request_data", "data_type": "reminders", "data": {json.dumps(all_reminders, default=str)} }}\n```'
                                )
                            # Ensure types are correct
                            try:
                                reminder_id = int(reminder_id)
                            except Exception as e:
                                print(
                                    f"ERROR: Invalid reminder_id: {reminder_id} ({e})"
                                )
                                return "Could not edit reminder: invalid reminder ID."

                            if reminder_id and new_message and new_remind_at:
                                try:
                                    print(
                                        f"[AI Edit] Attempting to update reminder: id={reminder_id}, new_message={new_message}, new_remind_at={new_remind_at}"
                                    )
                                    storage.update_reminder(
                                        reminder_id, new_message, new_remind_at
                                    )
                                    print(
                                        f"[AI Edit] Updated reminder in DB: id={reminder_id}"
                                    )
                                    # Fetch the updated reminder from the DB to ensure correct values
                                    updated = next(
                                        (
                                            r
                                            for r in storage.get_all_reminders()
                                            if r[0] == reminder_id
                                        ),
                                        None,
                                    )
                                    print(
                                        f"[AI Edit] Fetched from DB after update: {updated}"
                                    )
                                    if updated:
                                        updated_message = updated[1]
                                        updated_remind_at = updated[2]
                                        try:
                                            updated_remind_at_dt = (
                                                dateutil.parser.parse(updated_remind_at)
                                            )
                                            print(
                                                f"[AI Edit] Rescheduling with: id={reminder_id}, message={updated_message}, remind_at={updated_remind_at}"
                                            )
                                            scheduler.reschedule_reminder(
                                                reminder_id,
                                                updated_message,
                                                updated_remind_at_dt,
                                            )
                                        except Exception as sched_err:
                                            print(
                                                f"[Scheduler] Failed to reschedule reminder id={reminder_id}: {sched_err}"
                                            )
                                    else:
                                        print(
                                            f"[AI Edit] Reminder id={reminder_id} not found in DB after update."
                                        )
                                    print(
                                        f"DEBUG: update_reminder called with id={reminder_id}, message={new_message}, remind_at={new_remind_at}"
                                    )
                                except Exception as e:
                                    print(f"ERROR: update_reminder failed: {e}")
                                    print(f"[AI Edit] Exception during update: {e}")
                                    return "Could not edit reminder: database error."
                            else:
                                print("ERROR: Missing required fields for edit.")
                                return "Could not edit reminder: missing required information."
                        # Only create a new reminder if no action is present
                        elif (
                            isinstance(response_json, dict)
                            and response_json.get("is_reminder") is True
                            and response_json.get("reminder")
                        ):
                            reminder = response_json["reminder"]
                            message = reminder.get("message")
                            remind_at = reminder.get("remind_at")
                            if message and remind_at:
                                # Parse ISO datetime string to datetime object
                                remind_at_dt = dateutil.parser.isoparse(remind_at)
                                scheduler.schedule_reminder(message, remind_at_dt)
                        # Handle convo action
                        elif response_json.get("action") == "convo":
                            return response_json.get("ai_response", raw_answer)
                        # Handle GitHub actions
                        elif response_json.get("action") == "github_notifications":
                            notifications = self.github_integration.get_notifications()
                            if isinstance(notifications, list):
                                if not notifications:
                                    return "You have no new GitHub notifications."
                                return "Your GitHub notifications:\n" + "\n".join(
                                    f"- [{n['repository']}] {n['subject']} ({n['type']})"
                                    for n in notifications
                                )
                            return notifications.get(
                                "error", "Error fetching notifications."
                            )
                        elif response_json.get("action") == "github_prs":
                            prs = self.github_integration.get_pull_requests()
                            if isinstance(prs, list):
                                if not prs:
                                    return "You have no open GitHub pull requests."
                                return "Your open GitHub PRs:\n" + "\n".join(
                                    f"- [{pr['repo']}] {pr['title']} (#{pr['number']})"
                                    for pr in prs
                                )
                            return prs.get("error", "Error fetching pull requests.")
                        elif response_json.get("action") == "github_repos":
                            repos = self.github_integration.get_repos()
                            if isinstance(repos, list):
                                if not repos:
                                    return "You have no repositories."
                                # Always show full_name
                                return "Your repositories:\n" + "\n".join(
                                    f"- {repo['full_name']}: {repo['description'] or 'No description'}"
                                    for repo in repos
                                )
                            return repos.get("error", "Error fetching repositories.")
                        elif response_json.get("action") == "github_activity":
                            activity = self.github_integration.get_recent_activity()
                            if isinstance(activity, list):
                                if not activity:
                                    return "No recent GitHub activity."
                                return "Your recent GitHub activity:\n" + "\n".join(
                                    f"- [{a['repo']}] {a['type']} by {a['actor']} at {a['created_at']}"
                                    for a in activity
                                )
                            return activity.get("error", "Error fetching activity.")
                        elif response_json.get("action") == "github_prs_for_repo":
                            repo_name = response_json.get("repo")
                            user_filter = response_json.get("user")
                            if not repo_name:
                                return "No repository specified. Please provide the full repository name (owner/repo)."
                            # Defensive: If not full_name, try to resolve
                            if "/" not in repo_name:
                                repos = self.github_integration.get_repos()
                                matches = [
                                    r
                                    for r in repos
                                    if r["name"].lower() == repo_name.lower()
                                ]
                                if len(matches) == 1:
                                    repo_name = matches[0]["full_name"]
                                elif len(matches) > 1:
                                    return (
                                        f"Multiple repositories match '{repo_name}':\n"
                                        + "\n".join(
                                            f"- {r['full_name']}" for r in matches
                                        )
                                        + "\nPlease specify the full repository name (owner/repo)."
                                    )
                                else:
                                    return f"No repository found matching '{repo_name}'. Please specify the full repository name (owner/repo)."
                            prs = self.github_integration.get_pull_requests_for_repo(
                                repo_name, user=user_filter
                            )
                            if isinstance(prs, list):
                                if not prs:
                                    if user_filter:
                                        return f"You have no open pull requests in {repo_name} for user {user_filter}."
                                    return f"You have no open pull requests in {repo_name}."
                                if user_filter:
                                    return (
                                        f"Open PRs for {repo_name} (user: {user_filter}):\n"
                                        + "\n".join(
                                            f"- {pr['title']} (#{pr['number']})"
                                            for pr in prs
                                        )
                                    )
                                return f"Open PRs for {repo_name}:\n" + "\n".join(
                                    f"- {pr['title']} (#{pr['number']})" for pr in prs
                                )
                            return prs.get(
                                "error",
                                f"Error fetching pull requests for {repo_name}.",
                            )
                        return response_json.get("ai_response", raw_answer)
                    except Exception as e:
                        print("JSON parsing error:", e)
                        return raw_answer
                else:
                    # If no JSON block, just return the answer as before
                    return raw_answer
            else:
                return self.get_fallback_response(user_message)

        except Exception as e:
            print(f"Exception in AI client: {str(e)}")
            return self.get_fallback_response(user_message)

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
            getattr(self, "system_prompt", "")
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
        Use the existing get_response method to send the prompt to the backend.
        """
        return self.get_response(prompt)
