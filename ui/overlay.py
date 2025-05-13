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
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QPalette, QTextCursor
from core.ai_client import AIClient
from core import storage
from core import scheduler
import logging
import getpass
import datetime
import dateutil.parser


class AIWorker(QThread):
    """
    Worker thread for running AI queries without blocking the UI.
    """

    result_ready = pyqtSignal(str)

    def __init__(self, ai_client: AIClient, user_text: str) -> None:
        super().__init__()
        self.ai_client = ai_client
        self.user_text = user_text

    def run(self) -> None:
        response = self.ai_client.get_response(self.user_text)
        self.result_ready.emit(response)


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
        self._ai_worker: Optional[AIWorker] = None
        self._init_ui()

    def _init_ui(self) -> None:
        """
        Set up the UI layout and widgets for the overlay.
        """
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
        self.show()
        self.activateWindow()
        self.raise_()

    def hide_overlay(self) -> None:
        """
        Hide the overlay window.
        """
        self.hide()

    def _on_send_clicked(self) -> None:
        print("DEBUG: _on_send_clicked called")
        user_text = self.input_box.text().strip()
        print(f"DEBUG: user_text sent: '{user_text}'")
        if not user_text:
            return
        self.input_box.clear()
        self._append_user_message(user_text)
        self._append_ai_message("<i>Thinking...</i>")
        self.input_box.setDisabled(True)
        self.send_button.setDisabled(True)
        self._ai_worker = AIWorker(self.ai_client, user_text)
        self._ai_worker.result_ready.connect(self._on_ai_response)
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
        # Remove the last 'Thinking...' message if present
        cursor = self.response_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        last_block = cursor.selectedText()
        if "Thinking..." in last_block:
            cursor.removeSelectedText()
            cursor.deletePreviousChar()
            self.response_display.setTextCursor(cursor)
        # Extract ai_response from JSON if present
        import re, json

        match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)
        if match:
            try:
                response_json = json.loads(match.group(1))
                ai_message = response_json.get("ai_response", response)
            except Exception:
                ai_message = response
        else:
            ai_message = response
        self._append_ai_message(ai_message)

    def _on_ai_worker_finished(self) -> None:
        """
        Re-enable input after AI response is received.
        """
        self.input_box.setDisabled(False)
        self.send_button.setDisabled(False)
        self.input_box.setFocus()

    def _show_reminders_dialog(self) -> None:
        print("DEBUG: _show_reminders_dialog called")
        dlg = RemindersDialog(self)
        dlg.refresh_reminders()
        dlg.exec()

    # TODO: Add methods for integrating with the AI client and updating chat
