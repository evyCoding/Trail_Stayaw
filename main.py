from machine import Pin, SoftI2C, SPI, I2S
from ssd1306 import SSD1306_I2C
import os
import time
import sdcard

# Display dimensions
WIDTH = 128
HEIGHT = 64

# Define the pins for SDA and SCL (change as per your setup)
sda_pin = Pin(13)
scl_pin = Pin(14)

# Initialize I2C and SSD1306 display
i2c = SoftI2C(sda=sda_pin, scl=scl_pin, freq=200000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

def slide_text(oled, text, start_x, end_x, y, speed):
    """
    Function to slide text across the OLED display.
    
    :param oled: SSD1306_I2C instance
    :param text: Text to display
    :param start_x: Starting x position
    :param end_x: Ending x position
    :param y: y position of text
    :param speed: Delay between updates (lower is faster)
    """
    text_width = len(text) * 8

    for x in range(start_x, end_x - text_width, -1):
        oled.fill(0)  # Clear the display
        oled.text(text, x, y)  # Draw the text at the new position
        oled.show()  # Update the display
        time.sleep(speed)  # Wait before updating again

# Initialize SPI for SD card
sck_pin = Pin(2)
mosi_pin = Pin(3)
miso_pin = Pin(4)
spi = SPI(0, baudrate=1000000, polarity=0, phase=0, sck=sck_pin, mosi=mosi_pin, miso=miso_pin)
cs_pin = Pin(5, Pin.OUT)

# Initialize SD card
sd = sdcard.SDCard(spi, cs_pin)
vfs = os.VfsFat(sd)
os.mount(vfs, "/sd")

# Locate the first WAV file on the SD card
wav_file = None
files = os.listdir('/sd')

for file_name in files:
    if file_name.endswith('.wav'):
        wav_file = file_name
        break  # Found the first WAV file, exit loop

if wav_file is not None:
    print("First WAV file to play:", wav_file)
else:
    print("No WAV files found on SD card.")

# Initialize I2S interface for PCM5102A DAC
i2s = I2S(
    0,
    sck=Pin(16),
    ws=Pin(17),
    sd=Pin(18),
    mode=I2S.TX,
    bits=16,
    format=I2S.STEREO,
    rate=44100,
    ibuf=40000
)

# Function to play WAV data
def play_wav(file_path):
    with open(file_path, 'rb') as f:
        f.seek(44)  # Skip the WAV header
        while True:
            data = f.read(1024)
            if not data:
                break
            i2s.write(data)

# Function to display scrolling text on OLED
def main():
    if wav_file is None:
        display_text = "No WAV file found!"
    else:
        display_text = "Playing: " + wav_file

    # Display scrolling text on OLED
    for _ in range(1):  # Example to run the loop 10 times
        slide_text(oled, display_text, WIDTH, -len(display_text) * 8, 25, 0.05)  # Scroll text on OLED

    # Play WAV file if found
    if wav_file is not None:
        play_wav('/sd/' + wav_file)

# Clear the display initially
oled.fill(0)
oled.show()

# Start main program loop
main()
