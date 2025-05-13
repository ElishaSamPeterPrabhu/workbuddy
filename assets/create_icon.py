"""
Icon creation utility for WorkBuddy (Jarvis Assistant).

Generates the tray and overlay icons for the application.

TODO: Move this utility to /assets or /ui as appropriate.
"""

from PIL import Image, ImageDraw

# Create a 64x64 icon with WorkBuddy colors
icon = Image.new("RGBA", (64, 64), color=(52, 152, 219, 255))  # Blue background
draw = ImageDraw.Draw(icon)

# Draw a simple "W" letter
draw.polygon(
    [
        (10, 45),
        (20, 10),
        (30, 10),
        (32, 40),
        (42, 10),
        (52, 10),
        (54, 45),
        (44, 45),
        (42, 25),
        (32, 54),
        (22, 25),
        (20, 45),
    ],
    fill=(255, 255, 255, 255),
)

# Save the icon
icon.save("icon.png")

print("Icon created successfully!")
