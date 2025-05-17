"""
PyQt6 Overlay Chat Window for WorkBuddy (Jarvis Assistant).

This module provides a modern, floating assistant UI overlay with a dimmed background and a chat popup at the bottom of the screen.
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QDialog,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
    QFrame,
    QGraphicsDropShadowEffect,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QDateTimeEdit,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QCoreApplication, QTimer
from PyQt6.QtGui import QColor, QPalette, QTextCursor
from core.ai_client import AIClient
from core import storage
from core import scheduler
from core.ai_file_search_handler import AIFileSearchHandler
import logging
import getpass
import datetime
import dateutil.parser
import json
import re
import os
import io
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Union


class AIWorker(QThread):
    """
    Worker thread for running AI queries without blocking the UI.
    """

    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, ai_client: AIClient, user_text: str) -> None:
        super().__init__()
        self.ai_client = ai_client
        self.user_text = user_text
        self.timeout = 10  # Reduced from 15 to 10 seconds max wait for AI response
        self.should_cancel = False

    def run(self) -> None:
        print(f"DEBUG: AIWorker.run() - getting response for: {self.user_text}")
        try:
            # Use QTimer to implement a timeout mechanism
            from PyQt6.QtCore import QTimer, QEventLoop
            
            # Create local event loop
            loop = QEventLoop()
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(loop.quit)
            
            # Set up result variables
            response = None
            timed_out = False
            
            # Define the worker function that will run in this thread
            def get_ai_response():
                nonlocal response
                try:
                    if not self.should_cancel:
                        response = self.ai_client.get_response(self.user_text)
                except Exception as e:
                    print(f"ERROR in AIWorker: {str(e)}")
                    import traceback
                    print(traceback.format_exc())
                    response = json.dumps({
                        "ai_response": f"Sorry, I encountered an error: {str(e)}"
                    })
                finally:
                    if not self.should_cancel:
                        loop.quit()
            
            # Start the timer
            timer.start(self.timeout * 1000)  # Convert to milliseconds
            
            # Start the worker function in this thread
            QTimer.singleShot(0, get_ai_response)
            
            # Wait until either the timer times out or the function completes
            loop.exec()
            
            # Return immediately if cancelled
            if self.should_cancel:
                print("DEBUG: AIWorker cancelled, exiting immediately")
                return
                
            # Check if we timed out
            if timer.isActive():
                # Worker completed before timeout
                timer.stop()
            else:
                # We timed out
                timed_out = True
                print(f"DEBUG: AIWorker timed out after {self.timeout} seconds")
                response = json.dumps({
                    "ai_response": "I'm taking longer than expected to respond. Please try again with a simpler request."
                })
            
            # Process the response
            try:
                if response:
                    # Try parsing response as JSON
                    json_obj = json.loads(response)
                    print(f"DEBUG: AIWorker.run() - parsed response as JSON: {json_obj}")
                    # If it parses as JSON, wrap it in ```json ``` to signal it's JSON
                    self.result_ready.emit(f"```json\n{response}\n```")
                else:
                    # No response (should not happen with timeout mechanism)
                    self.result_ready.emit(json.dumps({
                        "ai_response": "Sorry, I wasn't able to generate a response."
                    }))
            except json.JSONDecodeError:
                # Not JSON, pass through as is
                print("DEBUG: AIWorker.run() - response is not JSON, passing through as is")
                self.result_ready.emit(response)
                
        except Exception as e:
            print(f"CRITICAL ERROR in AIWorker thread: {e}")
            import traceback
            print(traceback.format_exc())
            self.error_occurred.emit(f"Sorry, I encountered an unexpected error: {str(e)}")
            
    def cancel(self):
        """Cancel the worker thread operation."""
        self.should_cancel = True


class RemindersDialog(QDialog):
    """
    Dialog to display and manage reminders.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Reminders")
        self.setModal(True)
        self.setFixedSize(640, 400)
        self.setStyleSheet("background: rgba(20, 30, 50, 0.98); border-radius: 24px;")
        layout = QVBoxLayout(self)
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Message", "Time", "Status", "Edit", "Delete"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(
            "color: #e3eafc; background: #18243a; border-radius: 12px;"
        )
        layout.addWidget(self.table)
        self.refresh_reminders()

    def refresh_reminders(self) -> None:
        reminders = storage.get_all_reminders()
        self.table.setRowCount(len(reminders))
        for row, (reminder_id, message, remind_at, is_done) in enumerate(reminders):
            self.table.setItem(row, 0, QTableWidgetItem(message))
            # Format remind_at nicely
            try:
                dt = datetime.datetime.fromisoformat(remind_at)
                formatted_time = dt.strftime("%b %d, %Y, %I:%M %p")
            except Exception:
                formatted_time = remind_at
            self.table.setItem(row, 1, QTableWidgetItem(formatted_time))
            status = "Pending" if is_done == 0 else "Done"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(
                QColor("#8ab4f8") if is_done == 0 else QColor("#b23c3c")
            )
            self.table.setItem(row, 2, status_item)
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet(
                "background: #2a3959; color: #8ab4f8; border-radius: 8px;"
            )
            edit_btn.setEnabled(is_done == 0)
            edit_btn.clicked.connect(lambda _, rid=reminder_id: self.edit_reminder(rid))
            self.table.setCellWidget(row, 3, edit_btn)
            del_btn = QPushButton("Delete")
            del_btn.setStyleSheet(
                "background: #b23c3c; color: #fff; border-radius: 8px;"
            )
            del_btn.setEnabled(is_done == 0)
            del_btn.clicked.connect(
                lambda _, rid=reminder_id: self.delete_reminder(rid)
            )
            self.table.setCellWidget(row, 4, del_btn)

    def edit_reminder(self, reminder_id: int) -> None:
        """Show a dialog to edit the selected reminder and update it in storage."""
        # Fetch current reminder details
        reminders = storage.get_all_reminders()
        reminder = next((r for r in reminders if r[0] == reminder_id), None)
        if not reminder:
            QMessageBox.warning(self, "Error", "Reminder not found.")
            return
        old_message, old_remind_at = reminder[1], reminder[2]

        # Create dialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Edit Reminder")
        dlg.setModal(True)
        dlg.setFixedSize(400, 200)
        layout = QVBoxLayout(dlg)

        msg_label = QLabel("Message:", dlg)
        layout.addWidget(msg_label)
        msg_edit = QLineEdit(dlg)
        msg_edit.setText(old_message)
        layout.addWidget(msg_edit)

        time_label = QLabel("Remind At (YYYY-MM-DD HH:MM:SS):", dlg)
        layout.addWidget(time_label)
        time_edit = QDateTimeEdit(dlg)
        time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        try:
            dt = datetime.datetime.fromisoformat(old_remind_at)
            time_edit.setDateTime(dt)
        except Exception:
            time_edit.setDateTime(datetime.datetime.now())
        layout.addWidget(time_edit)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save", dlg)
        cancel_btn = QPushButton("Cancel", dlg)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        def on_save() -> None:
            new_message = msg_edit.text().strip()
            new_remind_at = time_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            if not new_message:
                QMessageBox.warning(dlg, "Validation Error", "Message cannot be empty.")
                return
            try:
                storage.update_reminder(reminder_id, new_message, new_remind_at)
                # Reschedule the reminder in APScheduler
                try:
                    new_remind_at_dt = dateutil.parser.parse(new_remind_at)
                    scheduler.reschedule_reminder(
                        reminder_id, new_message, new_remind_at_dt
                    )
                except Exception as sched_err:
                    logging.error(
                        f"[Scheduler] Failed to reschedule reminder id={reminder_id}: {sched_err}"
                    )
                # Log the edit
                user = getpass.getuser()
                logging.info(
                    f"[ReminderEdit] user={user} id={reminder_id} old_message={old_message} new_message={new_message} old_time={old_remind_at} new_time={new_remind_at} at={datetime.datetime.now().isoformat()}"
                )
                self.refresh_reminders()
                dlg.accept()
            except Exception as e:
                QMessageBox.critical(dlg, "Error", f"Failed to update reminder: {e}")

        save_btn.clicked.connect(on_save)
        cancel_btn.clicked.connect(dlg.reject)
        dlg.exec()

    def delete_reminder(self, reminder_id: int) -> None:
        confirm = QMessageBox.question(
            self,
            "Delete Reminder",
            "Are you sure you want to delete this reminder?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            storage.mark_reminder_done(reminder_id)
            self.refresh_reminders()


class OverlayWindow(QDialog):
    """
    Overlay chat window with dimmed background and floating chat popup.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the overlay window.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.ai_client = AIClient()
        self.file_search_handler = AIFileSearchHandler(self.ai_client)
        print("DEBUG: Connected AI client to file search handler")
        self._ai_worker: Optional[AIWorker] = None
        # Store last search results for context in follow-up queries
        self.last_search_results = []
        self.pending_search_command = None
        self.waiting_for_search_confirmation = False
        # Track the reminders dialog
        self.reminder_dialog: Optional[RemindersDialog] = None
        self._init_ui()

    def _init_ui(self) -> None:
        """
        Set up the UI layout and widgets for the overlay.
        """
        try:
            # Full-screen, semi-transparent dimmed background
            self.setGeometry(
                0, 0, self.screen().geometry().width(), self.screen().geometry().height()
            )

            # Main layout (transparent)
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)

            # Spacer to push chat popup to bottom
            main_layout.addStretch(1)

            # Chat popup frame
            self.chat_frame = QFrame(self)
            self.chat_frame.setObjectName("chatFrame")
            self.chat_frame.setFixedWidth(600)
            # Add glowing effect
            glow = QGraphicsDropShadowEffect(self.chat_frame)
            glow.setBlurRadius(48)
            glow.setColor(QColor(138, 180, 248, 180))  # Soft blue glow
            glow.setOffset(0, 0)
            self.chat_frame.setGraphicsEffect(glow)
            # Enhanced border radius
            self.chat_frame.setStyleSheet(
                """
                QFrame#chatFrame {
                    background: rgba(20, 30, 50, 0.98);
                    border-radius: 32px;
                    border: 2px solid #2a3959;
                }
                """
            )

            chat_layout = QVBoxLayout(self.chat_frame)
            chat_layout.setContentsMargins(24, 18, 24, 18)
            chat_layout.setSpacing(12)

            # Response display (read-only)
            self.response_display = QTextEdit(self.chat_frame)
            self.response_display.setReadOnly(True)
            self.response_display.setFixedHeight(90)
            self.response_display.setStyleSheet(
                "background: #18243a; color: #e3eafc; border: none; font-size: 13px; border-radius: 8px;"
            )
            self.response_display.setText(
                "Hi! How's it going? What can I assist you with today?"
            )
            chat_layout.addWidget(self.response_display)

            # Input row
            input_row = QHBoxLayout()
            input_row.setSpacing(8)

            self.input_box = QLineEdit(self.chat_frame)
            self.input_box.setPlaceholderText("Type something...")
            self.input_box.setStyleSheet(
                "background: #22304a; color: #e3eafc; border: none; font-size: 14px; border-radius: 8px; padding: 8px;"
            )
            self.input_box.returnPressed.connect(self._on_send_clicked)
            input_row.addWidget(self.input_box, 1)

            self.send_button = QPushButton("➤", self.chat_frame)
            self.send_button.setStyleSheet(
                "background: #2a3959; color: #8ab4f8; border: none; font-size: 18px; border-radius: 8px; padding: 8px 16px;"
            )
            self.send_button.clicked.connect(self._on_send_clicked)
            input_row.addWidget(self.send_button)

            # Add Reminders icon button (⏰) to the right of the input box
            self.reminders_icon_button = QPushButton("⏰", self.chat_frame)
            self.reminders_icon_button.setToolTip("Show all reminders")
            self.reminders_icon_button.setFixedSize(36, 36)
            self.reminders_icon_button.setStyleSheet(
                "background: #22304a; color: #8ab4f8; border: none; font-size: 20px; border-radius: 18px;"
            )
            self.reminders_icon_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.reminders_icon_button.setAutoDefault(False)
            self.reminders_icon_button.clicked.connect(self._show_reminders_dialog)
            input_row.addWidget(self.reminders_icon_button)

            chat_layout.addLayout(input_row)
            self.chat_frame.setLayout(chat_layout)

            # Center chat popup at bottom
            chat_popup_layout = QHBoxLayout()
            chat_popup_layout.addStretch(1)
            chat_popup_layout.addWidget(self.chat_frame)
            chat_popup_layout.addStretch(1)
            main_layout.addLayout(chat_popup_layout)
            main_layout.addSpacing(40)

            self.setLayout(main_layout)
            
            # Set focus policies to ensure proper tab order
            self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.input_box.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.send_button.setFocusPolicy(Qt.FocusPolicy.TabFocus)
            
            # Set tab order
            self.setTabOrder(self.input_box, self.send_button)
            self.setTabOrder(self.send_button, self.reminders_icon_button)
            
            print("DEBUG: UI initialization completed successfully")
        except Exception as e:
            import traceback
            print(f"ERROR in _init_ui: {e}")
            print(traceback.format_exc())
            # Create a minimal UI so the application doesn't crash completely
            minimal_layout = QVBoxLayout(self)
            error_label = QLabel(f"Error initializing UI: {str(e)}", self)
            error_label.setStyleSheet("color: white; background: rgba(255,0,0,128); padding: 20px;")
            minimal_layout.addWidget(error_label)
            self.setLayout(minimal_layout)

    def paintEvent(self, event) -> None:
        """
        Paint the semi-transparent dimmed background.
        """
        from PyQt6.QtGui import QPainter

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(10, 21, 37, int(255 * 0.75))  # 75% opacity
        painter.fillRect(self.rect(), color)
        super().paintEvent(event)

    def show_overlay(self) -> None:
        """
        Show the overlay window.
        """
        try:
            # First update the window size to match current screen
            self.setGeometry(0, 0, self.screen().geometry().width(), self.screen().geometry().height())
            
            # Ensure we're in the main thread for UI operations
            from PyQt6.QtCore import QThread
            if QThread.currentThread() is not QThread.currentThread():
                print("WARNING: show_overlay called from non-main thread")
                # Defer to main thread
                from PyQt6.QtCore import QMetaObject, Qt
                QMetaObject.invokeMethod(self, "show_overlay", Qt.ConnectionType.QueuedConnection)
                return
            
            # Show the window first
            self.show()
            self.activateWindow()
            self.raise_()
            
            # Force application to process events immediately
            from PyQt6.QtCore import QCoreApplication
            QCoreApplication.processEvents()
            
            # Set focus directly - not using a timer to avoid threading issues
            self.input_box.setFocus()
            
            print("DEBUG: Overlay window shown")
        except Exception as e:
            import traceback
            print(f"ERROR in show_overlay: {e}")
            print(traceback.format_exc())

    def hide_overlay(self) -> None:
        """
        Hide the overlay window.
        """
        try:
            # Ensure we're in the main thread for UI operations
            from PyQt6.QtCore import QThread
            if QThread.currentThread() is not QThread.currentThread():
                print("WARNING: hide_overlay called from non-main thread")
                # Defer to main thread
                from PyQt6.QtCore import QMetaObject, Qt
                QMetaObject.invokeMethod(self, "hide_overlay", Qt.ConnectionType.QueuedConnection)
                return
            
            # Check if the reminder dialog is open and close it
            if self.reminder_dialog and self.reminder_dialog.isVisible():
                print("DEBUG: Closing open reminder dialog")
                self.reminder_dialog.close()
                self.reminder_dialog = None
            
            # Simply hide the window - don't mess with the worker thread
            self.hide()
            
            # Force application to process events immediately
            from PyQt6.QtCore import QCoreApplication
            QCoreApplication.processEvents()
            
            print("DEBUG: Overlay window hidden")
        except Exception as e:
            import traceback
            print(f"ERROR in hide_overlay: {e}")
            print(traceback.format_exc())

    def toggle_visibility(self) -> None:
        """
        Toggle the visibility of the overlay window.
        
        This method is used as a callback for the global hotkey.
        """
        try:
            print("DEBUG: toggle_visibility called")
            
            # Ensure we're in the main thread for UI operations
            from PyQt6.QtCore import QThread
            if QThread.currentThread() is not QThread.currentThread():
                print("WARNING: toggle_visibility called from non-main thread")
                # Defer to main thread
                from PyQt6.QtCore import QMetaObject, Qt
                QMetaObject.invokeMethod(self, "toggle_visibility", Qt.ConnectionType.QueuedConnection)
                return
            
            # Simple visibility toggle with safeguards
            if self.isVisible():
                print("DEBUG: Window is visible, hiding")
                self.hide_overlay()
            else:
                print("DEBUG: Window is hidden, showing")
                self.show_overlay()
                
                # This second call to setFocus is crucial - needed for some systems
                # Force application to process events in between
                from PyQt6.QtCore import QCoreApplication
                QCoreApplication.processEvents()
                self.input_box.setFocus()
                
        except Exception as e:
            import traceback
            print(f"ERROR in toggle_visibility: {e}")
            print(traceback.format_exc())
            # Simplest recovery - just hide
            self.hide()

    def _on_send_clicked(self) -> None:
        print("DEBUG: _on_send_clicked called")
        user_text = self.input_box.text().strip()
        print(f"DEBUG: user_text sent: '{user_text}'")
        if not user_text:
            return
            
        # Store the user's text for context in reminder processing
        self.user_text = user_text
            
        # Let the AI handle all decisions naturally
        self.input_box.clear()
        self._append_user_message(user_text)
        self._append_ai_message("<i>Thinking...</i>")
        self.input_box.setDisabled(True)
        self.send_button.setDisabled(True)
        
        # Clean up any existing worker thread
        if hasattr(self, '_ai_worker') and self._ai_worker and self._ai_worker.isRunning():
            print("DEBUG: Cancelling previous AI worker")
            self._ai_worker.cancel()
        
        # Set up a watchdog timer to re-enable input after a maximum wait time
        from PyQt6.QtCore import QTimer
        if hasattr(self, 'input_watchdog') and self.input_watchdog.isActive():
            self.input_watchdog.stop()
        self.input_watchdog = QTimer(self)
        self.input_watchdog.setSingleShot(True)
        self.input_watchdog.timeout.connect(self._on_ai_worker_timeout)
        self.input_watchdog.start(15000)  # 15 seconds max wait (reduced from 20)
        
        # Start the AI worker
        self._ai_worker = AIWorker(self.ai_client, user_text)
        self._ai_worker.result_ready.connect(self._on_ai_response)
        self._ai_worker.error_occurred.connect(self._on_ai_worker_error)
        self._ai_worker.finished.connect(self._on_ai_worker_finished)
        self._ai_worker.start()

    def _append_user_message(self, text: str) -> None:
        """
        Append the user's message to the chat display.
        """
        self.response_display.append(f'<b style="color:#8ab4f8;">You:</b> {text}')

    def _append_ai_message(self, text: str) -> None:
        """
        Append the AI's message to the chat display.
        """
        self.response_display.append(f'<b style="color:#fbbc05;">TARS:</b> {text}')

    def _on_ai_response(self, response: str) -> None:
        """
        Display the AI's response in the chat display.
        """
        print(f"DEBUG: _on_ai_response received raw response: {response[:100]}...")
        
        # Remove the last 'Thinking...' message if present
        cursor = self.response_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        last_block = cursor.selectedText()
        if "Thinking..." in last_block:
            cursor.removeSelectedText()
            cursor.deletePreviousChar()
            self.response_display.setTextCursor(cursor)
        
        # Clear out any markdown code block formatting, etc.
        # This is the main fix to handle the JSON formatting issue
        cleaned_response = response
        
        # First look for ```json blocks specifically
        json_block_pattern = r'```json\s*(.*?)\s*```'
        json_blocks = re.findall(json_block_pattern, response, re.DOTALL)
        if json_blocks:
            print(f"DEBUG: Found {len(json_blocks)} JSON code blocks")
            # Use the first JSON block found
            cleaned_response = json_blocks[0].strip()
            print(f"DEBUG: Extracted JSON from code block: {cleaned_response[:100]}...")
        else:
            # Try other patterns to find JSON objects
            code_block_pattern = r'```\s*(.*?)\s*```'
            code_blocks = re.findall(code_block_pattern, response, re.DOTALL)
            if code_blocks:
                # Check if any code block contains valid JSON
                for block in code_blocks:
                    try:
                        # If this parses as JSON, use it
                        json.loads(block.strip())
                        cleaned_response = block.strip()
                        print(f"DEBUG: Found JSON in general code block: {cleaned_response[:100]}...")
                        break
                    except:
                        continue
        
        # Try to parse the cleaned response as JSON
        try:
            response_json = json.loads(cleaned_response)
            print(f"DEBUG: Successfully parsed JSON: {response_json}")
            
            # Process JSON actions and get user-facing message
            if "ai_response" in response_json:
                # Extract the user-facing message
                user_message = response_json["ai_response"]
                
                # Process any actions in the background
                self._process_json_actions(response_json)
                
                # Show only the user-facing message
                self._append_ai_message(user_message)
                return
            
            # Handle special case for reminder data requests
            if "action" in response_json and response_json["action"] == "request_data" and response_json.get("data_type") == "reminders":
                self._handle_reminder_data_request(response_json)
                return
        except json.JSONDecodeError:
            print(f"DEBUG: Failed to parse as JSON: {cleaned_response[:100]}...")
            # If it's not valid JSON, just display the original response
            self._append_ai_message(response)
    
    def _handle_reminder_data_request(self, request_json: dict) -> None:
        """
        Process a request for reminder data from the AI.
        
        Args:
            request_json: The parsed JSON request from the AI
        """
        print("DEBUG: Processing request for reminder data")
        # Get all reminders from storage
        reminders = storage.get_all_reminders()
        
        if not reminders:
            self._append_ai_message("You don't have any reminders to edit.")
            return
        
        # Format reminders for the AI
        formatted_reminders = []
        for reminder_id, message, remind_at, is_done in reminders:
            if is_done == 0:  # Only include pending reminders
                try:
                    dt = datetime.datetime.fromisoformat(remind_at)
                    formatted_time = dt.strftime("%b %d, %Y, %I:%M %p")
                except:
                    formatted_time = remind_at
                
                formatted_reminders.append({
                    "id": reminder_id,
                    "message": message,
                    "time": formatted_time,
                    "original_time": remind_at
                })
        
        if not formatted_reminders:
            self._append_ai_message("You don't have any pending reminders to edit.")
            return
        
        # Get the original user text
        original_user_text = self.user_text if hasattr(self, 'user_text') else ""
        print(f"DEBUG: Original user request was: {original_user_text}")
        
        # Create an AI request with the original user message and the reminders data
        ai_request = f"{original_user_text}\n\nAVAILABLE_REMINDERS: {json.dumps(formatted_reminders)}"
        print(f"DEBUG: Sending reminders data to AI: {ai_request[:100]}...")
        
        # Process the request with the AI to get the proper edit action
        try:
            ai_response = self.ai_client.get_response(ai_request)
            print(f"DEBUG: AI response with reminders data: {ai_response[:100]}...")
            
            # Process the AI's response with the new JSON handling logic
            self._on_ai_response(ai_response)
        except Exception as e:
            print(f"ERROR getting AI decision for reminders: {e}")
            # Fall back to showing the reminders list
            reminder_list = "\n".join([f"{i+1}. {r['message']} (at {r['time']})" for i, r in enumerate(formatted_reminders)])
            self._append_ai_message(f"Here are your pending reminders. Please specify which one you'd like to edit:\n\n{reminder_list}")
            
        return

    def _on_ai_worker_timeout(self) -> None:
        """Handle case where AI worker hasn't responded within the maximum wait time."""
        print("DEBUG: AI worker timeout triggered - forcing UI to re-enable")
        if self._ai_worker and self._ai_worker.isRunning():
            # Don't wait for the worker, just re-enable the UI
            # The thread will eventually finish or be cleaned up later
            print("WARNING: AI worker still running after timeout")
        
        cursor = self.response_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        last_block = cursor.selectedText()
        if "Thinking..." in last_block:
            cursor.removeSelectedText()
            cursor.deletePreviousChar()
            self.response_display.setTextCursor(cursor)
            self._append_ai_message("I'm taking longer than expected. The UI has been re-enabled so you can continue working.")
        
        # Re-enable input
        self.input_box.setDisabled(False)
        self.send_button.setDisabled(False)
        self.input_box.setFocus()

    def _on_ai_worker_error(self, error_message: str) -> None:
        """Handle errors reported by the AI worker thread."""
        print(f"DEBUG: AI worker reported error: {error_message}")
        cursor = self.response_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        last_block = cursor.selectedText()
        if "Thinking..." in last_block:
            cursor.removeSelectedText()
            cursor.deletePreviousChar()
            self.response_display.setTextCursor(cursor)
        
        self._append_ai_message(error_message)
        
        # Re-enable input
        self.input_box.setDisabled(False)
        self.send_button.setDisabled(False)
        self.input_box.setFocus()

    def _on_ai_worker_finished(self) -> None:
        """
        Re-enable input after AI response is received.
        """
        print("DEBUG: AI worker thread finished")
        # Cancel the watchdog timer
        if hasattr(self, 'input_watchdog') and self.input_watchdog.isActive():
            self.input_watchdog.stop()
        
        self.input_box.setDisabled(False)
        self.send_button.setDisabled(False)
        self.input_box.setFocus()

    def _show_reminders_dialog(self) -> None:
        print("DEBUG: _show_reminders_dialog called")
        self.reminder_dialog = RemindersDialog(self)
        self.reminder_dialog.refresh_reminders()
        self.reminder_dialog.exec()
        # Reset the reference after dialog is closed
        self.reminder_dialog = None

    def _run_extended_search(self) -> None:
        """
        Run the extended search based on the pending command.
        This is called when the user confirms they want to continue searching.
        """
        try:
            if not self.pending_search_command:
                print("ERROR: No pending search command to continue")
                self.result_ready.emit("I'm sorry, I lost track of what we were searching for. Could you please try again?")
                return
                
            # Call the continue_search method to perform extended search
            results = self.file_search_handler.continue_search(self.pending_search_command)
            print(f"DEBUG: Extended search results: {results}")
            
            # Process results similar to regular search
            if results.get("success"):
                pattern = self.pending_search_command.get("pattern", "")
                directory = self.pending_search_command.get("directory", "")
                
                if results.get("count", 0) > 0 and "files" in results:
                    # Store results for future reference
                    self.last_search_results = results["files"]
                    
                    # Create a simple string summary for AI context
                    found_files_string = ""
                    if len(results["files"]) == 1:
                        filepath = results["files"][0]
                        filename = os.path.basename(filepath)
                        directory = os.path.dirname(filepath)
                        found_files_string = f"Found the file '{filename}' at location: {filepath}"
                    else:
                        found_files_string = f"Found {len(results['files'])} files matching '{pattern}' in {directory}"
                        
                    # Save context for follow-up questions
                    self.ai_client.last_search_context_str = found_files_string
                    
                    # Format files for display
                    files_list = []
                    for file_path in results["files"][:10]:
                        filename = os.path.basename(file_path)
                        directory = os.path.dirname(file_path)
                        files_list.append(f"- {filename} (located in {directory})")
                        
                    if len(results["files"]) > 10:
                        files_list.append(f"...and {len(results['files']) - 10} more files")
                    
                    files_text = "\n".join(files_list)
                    response = f"After a more extensive search, I {found_files_string}\n\n{files_text}"
                else:
                    response = f"I've completed a more extensive search, but I still couldn't find any files matching '{pattern}' in {directory}."
            else:
                response = f"The extended search encountered an error: {results.get('error', 'Unknown error')}"
                
            # Clear the pending command
            self.pending_search_command = None
            
            # Update the UI with results
            self._append_ai_message(response)
            
        except Exception as e:
            import traceback
            print(f"ERROR in extended search: {e}")
            print(traceback.format_exc())
            self._append_ai_message(f"Sorry, there was an error during the extended search: {str(e)}")
            self.pending_search_command = None

    def _process_json_actions(self, response_json: dict) -> None:
        """
        Process any actions in the JSON response in the background.
        This allows us to handle reminder creation, editing, etc. without
        showing the raw JSON to the user.
        
        Args:
            response_json: The parsed JSON response from the AI
        """
        try:
            # Process reminder-specific actions
            if "action" in response_json:
                action = response_json["action"]
                
                # Handle reminder creation
                if action == "create" and response_json.get("is_reminder") == True and "reminder" in response_json:
                    reminder = response_json["reminder"]
                    message = reminder.get("message", "")
                    remind_at_str = reminder.get("remind_at", "")
                    
                    try:
                        # Parse the ISO datetime string
                        remind_at = dateutil.parser.parse(remind_at_str)
                        # Schedule the reminder
                        reminder_id = scheduler.schedule_reminder(message, remind_at)
                        print(f"DEBUG: Created reminder id={reminder_id}: {message} at {remind_at}")
                    except Exception as e:
                        print(f"ERROR creating reminder: {e}")
                
                # Handle reminder editing
                elif action == "edit" and "reminder_id" in response_json:
                    reminder_id = response_json.get("reminder_id")
                    new_message = response_json.get("new_message", "")
                    new_remind_at_str = response_json.get("new_remind_at", "")
                    
                    print(f"DEBUG: Processing edit action for reminder_id={reminder_id}")
                    print(f"DEBUG: Edit details - new_message='{new_message}', new_time='{new_remind_at_str}'")
                    
                    try:
                        # Parse the new time if provided
                        if new_remind_at_str:
                            print(f"DEBUG: Attempting to parse datetime: {new_remind_at_str}")
                            new_remind_at = dateutil.parser.parse(new_remind_at_str)
                            formatted_time = new_remind_at.strftime("%Y-%m-%d %H:%M:%S")
                            print(f"DEBUG: Successfully parsed datetime to: {formatted_time}")
                            
                            # Check if the reminder exists before updating
                            all_reminders = storage.get_all_reminders()
                            print(f"DEBUG: All reminders in DB: {all_reminders}")
                            reminder = next((r for r in all_reminders if r[0] == reminder_id), None)
                            if not reminder:
                                print(f"ERROR: Reminder with ID {reminder_id} not found in database")
                                return
                                
                            print(f"DEBUG: Found existing reminder: {reminder}")
                            
                            # Update the reminder in storage and reschedule
                            print(f"DEBUG: Calling storage.update_reminder({reminder_id}, {new_message}, {formatted_time})")
                            storage.update_reminder(reminder_id, new_message, formatted_time)
                            
                            print(f"DEBUG: Calling scheduler.reschedule_reminder({reminder_id}, {new_message}, {new_remind_at})")
                            scheduler.reschedule_reminder(reminder_id, new_message, new_remind_at)
                            
                            print(f"DEBUG: Successfully updated reminder id={reminder_id}")
                        else:
                            # If no new time, just update the message
                            all_reminders = storage.get_all_reminders()
                            reminder = next((r for r in all_reminders if r[0] == reminder_id), None)
                            if reminder:
                                storage.update_reminder(reminder_id, new_message, reminder[2])
                                print(f"DEBUG: Updated reminder id={reminder_id} message only")
                            else:
                                print(f"ERROR: Reminder with ID {reminder_id} not found in database")
                    except ValueError as ve:
                        print(f"ERROR parsing datetime: {ve}")
                    except Exception as e:
                        print(f"ERROR updating reminder: {str(e)}")
                        import traceback
                        print(traceback.format_exc())
                
                # Handle reminder deletion
                elif action == "delete" and "reminder_id" in response_json:
                    reminder_id = response_json.get("reminder_id")
                    try:
                        storage.mark_reminder_done(reminder_id)
                        scheduler.cancel_reminder(reminder_id)
                        print(f"DEBUG: Deleted reminder id={reminder_id}")
                    except Exception as e:
                        print(f"ERROR deleting reminder: {e}")
                
            # Process file search actions if present
            if "file_search" in response_json:
                file_search_cmd = response_json["file_search"]
                if isinstance(file_search_cmd, dict) and "action" in file_search_cmd:
                    print(f"DEBUG: Processing background file search command: {file_search_cmd}")
                    # This will be processed in the main method
        except Exception as e:
            print(f"ERROR in _process_json_actions: {e}")
            import traceback
            print(traceback.format_exc())

    # TODO: Add methods for integrating with the AI client and updating chat
