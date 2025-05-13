"""
Legacy Tkinter UI for WorkBuddy (Jarvis Assistant).

This module provided the original overlay and chat UI using Tkinter.

TODO: Migrate all UI logic to /ui/overlay.py and related PyQt6 modules.
"""

import tkinter as tk
import threading
import sys
import os
from ai_client import AIClient
from PIL import Image, ImageTk


class WorkBuddyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WorkBuddy")

        # Make window frameless
        self.root.overrideredirect(True)

        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Window dimensions
        self.window_width = int(self.screen_width * 0.6)
        self.window_height = 180

        # Position window
        x_position = (self.screen_width - self.window_width) // 2
        y_position = self.screen_height - self.window_height - 50

        # Set window geometry
        self.root.geometry(
            f"{self.window_width}x{self.window_height}+{x_position}+{y_position}"
        )

        # Initialize AI client
        self.ai_client = AIClient()

        # Background image path
        self.bg_image_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "blue_waves_bg.png"
        )

        # Configure a solid background color for the root
        self.root.configure(bg="#0a1525")

        # ------ Create UI Elements ------

        # If we have a background image, load and display it
        if os.path.exists(self.bg_image_path):
            try:
                # Load the background image
                bg_image = Image.open(self.bg_image_path)
                bg_image = bg_image.resize(
                    (self.window_width, self.window_height), Image.LANCZOS
                )
                self.bg_photo = ImageTk.PhotoImage(bg_image)

                # Create a label to display the background
                self.bg_label = tk.Label(self.root, image=self.bg_photo)
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print(f"Error loading background: {e}")

        # Create a dark overlay frame
        self.overlay = tk.Frame(self.root, bg="#0a1525")
        self.overlay.place(x=0, y=0, relwidth=1, relheight=1)
        self.overlay.configure(bg="#0a1525", bd=0)
        self.overlay.attributes = {
            "alpha": 0.7
        }  # This doesn't actually work, just a visual note

        # Close button - X in the top-right corner
        self.close_button = tk.Button(
            self.overlay,
            text="×",
            font=("Arial", 12),
            fg="white",
            bg="#0a1525",
            bd=0,
            activebackground="#0a1525",
            activeforeground="#cccccc",
            command=self.hide_app,
        )
        self.close_button.place(x=self.window_width - 30, y=5)

        # Create a text widget for displaying AI responses
        self.response_display = tk.Text(
            self.overlay,
            font=("Arial", 10),
            fg="white",
            bg="#0a1525",
            bd=0,
            highlightthickness=0,
            height=5,
            width=70,
            wrap=tk.WORD,
        )
        self.response_display.place(x=20, y=30, width=self.window_width - 40)
        self.response_display.insert(
            tk.END, "Hi! How's it going? What can I assist you with today?"
        )
        self.response_display.configure(state="disabled")  # Make it read-only

        # Create a frame for input area
        self.input_area = tk.Frame(self.overlay, bg="#13213d", bd=0)
        self.input_area.place(
            x=20, y=self.window_height - 60, width=self.window_width - 40, height=40
        )

        # Create the input box
        self.user_input = tk.Entry(
            self.input_area,
            font=("Arial", 12),
            fg="white",
            bg="#13213d",
            bd=0,
            insertbackground="white",  # cursor color
            highlightthickness=0,
        )
        self.user_input.place(x=10, y=0, width=self.window_width - 110, height=40)
        self.user_input.bind("<Return>", self.send_message)
        self.user_input.bind("<Escape>", lambda e: self.hide_app())

        # Add placeholder text
        self.placeholder_text = "Type something..."
        self.user_input.insert(0, self.placeholder_text)
        self.user_input.bind("<FocusIn>", self.on_entry_click)
        self.user_input.bind("<FocusOut>", self.on_focus_out)

        # Add the mic button
        self.mic_button = tk.Button(
            self.input_area,
            text="🎤",
            font=("Arial", 14),
            fg="white",
            bg="#13213d",
            bd=0,
            activebackground="#1e2e4a",
            activeforeground="white",
            command=self.activate_voice_input,
        )
        self.mic_button.place(x=self.window_width - 100, y=0, width=30, height=40)

        # Add the send button
        self.send_button = tk.Button(
            self.input_area,
            text="➤",
            font=("Arial", 14),
            fg="#8ab4f8",
            bg="#13213d",
            bd=0,
            activebackground="#1e2e4a",
            activeforeground="#8ab4f8",
            command=self.send_message,
        )
        self.send_button.place(x=self.window_width - 70, y=0, width=30, height=40)

        # Make window draggable
        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<ButtonRelease-1>", self.stop_move)
        self.root.bind("<B1-Motion>", self.on_motion)

        # Setup system tray
        self.setup_system_tray()

    def on_entry_click(self, event):
        """Clear placeholder text when clicked"""
        if self.user_input.get() == self.placeholder_text:
            self.user_input.delete(0, tk.END)
            self.user_input.config(fg="white")

    def on_focus_out(self, event):
        """Restore placeholder text if empty"""
        if self.user_input.get() == "":
            self.user_input.insert(0, self.placeholder_text)
            self.user_input.config(fg="gray70")

    def activate_voice_input(self):
        """Simulate voice input activation"""
        self.user_input.delete(0, tk.END)
        self.user_input.insert(0, "Listening...")
        self.user_input.config(fg="#3498db")
        self.root.after(2000, lambda: self.user_input.delete(0, tk.END))
        self.root.after(2000, lambda: self.user_input.config(fg="white"))

    def start_move(self, event):
        """Start window drag operation"""
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        """Stop window drag operation"""
        self.x = None
        self.y = None

    def on_motion(self, event):
        """Handle window movement"""
        if hasattr(self, "x") and hasattr(self, "y"):
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")

    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        try:
            import pystray
            from PIL import Image, ImageDraw

            # Icon path (same as used for window icon)
            self.icon_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "icon.png"
            )

            # Create icon - use default if icon.png is not available
            icon_image = None
            if os.path.exists(self.icon_path):
                icon_image = Image.open(self.icon_path)
            else:
                # Create a simple icon if no icon file
                icon_image = Image.new("RGB", (64, 64), color=(52, 152, 219))
                d = ImageDraw.Draw(icon_image)
                d.rectangle((20, 20, 44, 44), fill=(255, 255, 255))

            # Define menu items
            def show_window(icon, item):
                self.root.after(0, self.show_app)

            def hide_window(icon, item):
                self.root.after(0, self.hide_app)

            def exit_app(icon, item):
                icon.stop()
                self.root.after(0, self.root.destroy)

            # Create menu
            menu = pystray.Menu(
                pystray.MenuItem("Show Input", show_window),
                pystray.MenuItem("Hide", hide_window),
                pystray.MenuItem("Exit", exit_app),
            )

            # Create and run icon in a separate thread
            self.icon = pystray.Icon("workbuddy", icon_image, "WorkBuddy", menu)
            threading.Thread(target=self.icon.run, daemon=True).start()

        except ImportError as e:
            print(f"Error setting up system tray: {e}")
            # If system tray setup fails, make the window visible
            self.root.deiconify()

    def show_app(self):
        """Show the main window"""
        self.root.deiconify()
        self.root.attributes("-topmost", True)
        self.root.focus_force()
        self.user_input.focus_set()
        self.root.after(100, lambda: self.root.attributes("-topmost", False))

    def hide_app(self):
        """Hide the window"""
        self.root.withdraw()

    def update_response(self, text):
        """Update the response display"""
        # Enable text widget for editing
        self.response_display.configure(state="normal")

        # Clear current text and insert new response
        self.response_display.delete(1.0, tk.END)
        self.response_display.insert(tk.END, text)

        # Make read-only again
        self.response_display.configure(state="disabled")

        # Clear the input field and set focus
        self.user_input.delete(0, tk.END)
        self.user_input.focus_set()

    def send_message(self, event=None):
        """Process user input and get AI response"""
        # Get user input
        user_message = self.user_input.get().strip()
        if not user_message or user_message == self.placeholder_text:
            return

        # Show "Thinking..." state
        self.update_response("Thinking...")

        # Process in background thread
        def process_response():
            try:
                # Get response from AI
                response = self.ai_client.get_response(user_message)

                # Update UI in main thread
                self.root.after(0, lambda: self.update_response(response))
                self.root.after(100, lambda: self.user_input.focus_set())
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                self.root.after(0, lambda: self.update_response(error_msg))
                self.root.after(100, lambda: self.user_input.focus_set())

        # Start processing thread
        threading.Thread(target=process_response).start()


def main():
    root = tk.Tk()
    app = WorkBuddyApp(root)

    # Show the application after a brief delay
    root.after(500, app.show_app)

    root.mainloop()


if __name__ == "__main__":
    main()
