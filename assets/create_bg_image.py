from PIL import Image, ImageDraw
import os
import math
import random


def create_blue_waves_bg(width=1200, height=800, filename="blue_waves_bg.png"):
    """Create a blue waves background image"""
    # Create a new image with dark blue background
    img = Image.new("RGB", (width, height), color=(10, 21, 37))
    draw = ImageDraw.Draw(img)

    # Define colors for waves
    wave_colors = [
        (26, 60, 125),  # Light blue
        (22, 47, 98),  # Medium blue
        (18, 40, 85),  # Darker blue
        (15, 32, 67),  # Very dark blue
    ]

    # Draw multiple waves
    for color_idx, color in enumerate(wave_colors):
        # Multiple waves per color with different phases and frequencies
        for i in range(3):
            frequency = random.uniform(0.004, 0.01)
            phase = random.uniform(0, 2 * math.pi)
            amplitude = random.randint(10, 30)
            thickness = random.randint(30, 50)

            # Draw the wave
            for x in range(0, width, 2):
                for w in range(thickness):
                    offset = color_idx * 150  # Offset each color group
                    y_base = offset + int(amplitude * math.sin(frequency * x + phase))
                    y = height - y_base - w - 100

                    # Only draw if in bounds
                    if 0 <= y < height:
                        # Apply a slight gradient within the wave
                        r, g, b = color
                        factor = 1.0 - (w / thickness) * 0.3
                        c = (int(r * factor), int(g * factor), int(b * factor))
                        draw.point((x, y), fill=c)

    # Add some random bright blue dots to simulate light reflections
    for _ in range(200):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        size = random.randint(1, 3)
        brightness = random.randint(150, 255)
        draw.ellipse((x, y, x + size, y + size), fill=(30, 80, brightness))

    # Save the image
    img.save(filename)
    print(f"Background image created: {filename}")
    return filename


if __name__ == "__main__":
    # Create the image in the current directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "blue_waves_bg.png")
    create_blue_waves_bg(filename=output_file)
