from PIL import ImageGrab
from PIL import ImageColor
import tkinter as tk
from tkinter import ttk
from tkinter.colorchooser import askcolor
import time
import serial
from serial.tools import list_ports
import math
import os
import sys
import threading
baud_rate = 115200
capture_width = 1920
capture_height = 1080
downsample_factor = 8
sw=0

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')
def clear_last_line():
    sys.stdout.write("\033[F")  # Move cursor up one line
    sys.stdout.write("\033[K")  # Clear to the end of line
clear_console()
print(f"===================================================================")
print(f"=========      RGB LED AMBIENT LIGHSYNC WITH ARDUINO      =========")
print(f"===================================================================")
print(f"Press CTRL+C to QUIT.")

def find_arduino_port():
    arduino_ports = [
        p.device
        for p in list_ports.comports()
        if "CH340" in p.description or "ARDUINO" in p.description]
    if not arduino_ports:
        raise Exception("Arduino not found. Make sure it's connected.")
    return arduino_ports[0]

try:
    arduino_port = find_arduino_port()
    ser = serial.Serial(arduino_port, baud_rate, timeout=2)
    print(f"Connected to Arduino on {arduino_port}")
except Exception as e:
    print(f"Failed to connect to Arduino: {e}")

class RGBSync(tk.Tk):

    def __init__(self):
        super().__init__()
        time.sleep(2)
        white_color = (100,100,100)
        color_data = ','.join(map(str, white_color)) + '\n'
        ser.write(color_data.encode())
        print("Restarting Arduino...")
    
        self.title("RGBSync")
        self.geometry("250x300")

        label = tk.Label(self, text="Select an Option:")
        label.pack(pady=10)

        options = ["Ambient Lighting", "Real Life Flashbang", "Manual HEX", "Color Fade"]
        self.choice_var = tk.StringVar()
        dropdown = ttk.Combobox(self, textvariable=self.choice_var, values=options)
        dropdown.pack()

        button = tk.Button(self, text="Select", command=self.select_option)
        button.pack(pady=10)
        self.exit_event = threading.Event()
        self.active_thread=None
        sw=0






    def get_average_color(self,image,mode):
        r_total = 0
        g_total = 0
        b_total = 0
        total_pixels = 0

        for y in range(0, image.height, downsample_factor):
            for x in range(0, image.width, downsample_factor):
                pixel = image.getpixel((x, y))
                r, g, b = pixel
                r_total += r
                g_total += g
                b_total += b
                total_pixels += 1

        avg_r = r_total // total_pixels
        avg_g = g_total // total_pixels
        avg_b = b_total // total_pixels

        print(f"Original: [{avg_r:03}, {avg_g:03}, {avg_b:03}] | ", end="")
        if avg_r+avg_g+avg_b>500:
            avg_r = int(255*(avg_r/255)**(1/2.2))
            avg_g = int(255*(avg_g/255)**(1/2.2))
            avg_b = int(255*(avg_b/255)**(1/2.2))
            print("\033[93mGAMMA HI\033[0m | ", end="")

        elif avg_r+avg_g+avg_b<50:
            avg_r = int(255*(avg_r/255)**(1.5))
            avg_g = int(255*(avg_g/255)**(1.5))
            avg_b = int(255*(avg_b/255)**(1.5))
            print("\033[91mGAMMA LO\033[0m | ", end="")


        else:
            print("\033[92mGAMMA NA\033[0m | ", end="")
        if mode==1:
            if avg_r>120 and avg_g>120 and avg_b>120:
                avr_r=255
                avr_g=255
                avr_b=255
            else: 
                avg_r=0
                avg_g=0
                avg_b=0

        return avg_r, avg_g, avg_b
    def ambientlighting(self,mode):
        print(f"Capture area = {capture_width}*{capture_height}")
        print(f"Downsample Factor = {downsample_factor}")
        while self.sw==1:
            screenshot = ImageGrab.grab(bbox=(0, 0, capture_width, capture_height))  # Capture a smaller portion of the screen
            screenshot = screenshot.resize((capture_width // downsample_factor, capture_height // downsample_factor))
            average_color = self.get_average_color(screenshot,mode)
            print(f"Normalized: [{average_color[0]:03}, {average_color[1]:03}, {average_color[2]:03}]")
            clear_last_line()
            # Send the adjusted color values to Arduino
            color_data = ','.join(map(str, average_color)) + '\n'
            ser.write(color_data.encode())
            time.sleep(0)  # Adjust the delay as needed
    def hexpicker(self):
        color = askcolor()[1]  # Get the selected color in the format "#RRGGBB"
        rgb=ImageColor.getrgb(color)
        color_data = ','.join(map(str, rgb)) + '\n'
        ser.write(color_data.encode())
    
    


    import time

    def color_fade(self):
    # Define the colors of the rainbow spectrum
        rainbow_colors = [
            (255, 000, 000),     # Red
            (255, 255, 000),   # Yellow
            (000, 255, 000),     # Green
            (000, 255, 255),   # Blue
            (000, 000, 255),     # Indigo
            (255, 000, 255)    # Violet
        ]
        delay=1
        # Define the number of steps for each color transition
        num_steps = 100  # Adjust this value for the desired duration of each color
        self.delay_label = tk.Label(self, text="Rate:")
        self.delay_label.pack()
        self.delay_var = tk.IntVar()  # Variable to bind to the slider value
        self.delay_slider = tk.Scale(self, from_=0.1, to=10, orient="horizontal", variable=delay)
        self.delay_slider.pack()
        #self.delay_var.set(1)  # Set an initial delay value"""
        # Loop through the rainbow colors and back to red
        while True:
            for i in range(len(rainbow_colors)):
                if self.sw==0:
                    self.delay_label.pack_forget()
                    self.delay_slider.pack_forget()
                    break
                start_color = rainbow_colors[i]
                end_color = rainbow_colors[(i + 1) % len(rainbow_colors)]  # Circular loop

                # Calculate the step size for each color channel
                step_size = tuple(
                    (end - start) / num_steps
                    for start, end in zip(start_color, end_color)
                )

                # Perform the color transition
                for step in range(num_steps):
                    if self.sw==0:
                        break
                    # Calculate the current color
                    current_color = tuple(
                        int(start + step * step_size[index])
                        for index, start in enumerate(start_color)
                    )

                    # Send the current color to the Arduino
                    color_data = ','.join(map(str, current_color)) + '\n'
                    ser.write(color_data.encode())

                    # Sleep for a short duration to control the fade speed
                    time.sleep(1/delay)  # Adjust this value for the desired speed

            # Ensure the final color is red
            color_data = ','.join(map(str, (255, 0, 0))) + '\n'
            ser.write(color_data.encode())



    


    def stop_thread(self):
        self.sw=0
        time.sleep(0.5)
        self.sw=1
    def select_option(self):
            choice = self.choice_var.get()
            if choice == "Ambient Lighting":
                self.stop_thread()
                active_thread = threading.Thread(target=self.ambientlighting,args=(0,))
                active_thread.start()
            elif choice == "Real Life Flashbang":
                self.stop_thread()
                active_thread = threading.Thread(target=self.ambientlighting,args=(1,))
                active_thread.start()
            elif choice == "Manual HEX":
                self.stop_thread()
                active_thread = threading.Thread(target=self.hexpicker)
                active_thread.start()
            elif choice == "Color Fade":
                self.stop_thread()
                active_thread = threading.Thread(target=self.color_fade)
                active_thread.start()


if __name__ == "__main__":
    appx = RGBSync()
    appx.mainloop()
