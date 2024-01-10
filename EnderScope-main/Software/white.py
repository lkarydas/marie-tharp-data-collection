import board
import neopixel
import time

# Set up NeoPixel strip
num_pixels = 16  # Change this to match the number of pixels in your NeoPixel ring
pixel_pin = board.D18  # GPIO pin D18 on Raspberry Pi
ORDER = neopixel.RGBW  # NeoPixel color order (RGBW for NeoPixel RGBW strips)

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER)

def set_white_brightness(brightness):
    for i in range(num_pixels):
        pixels[i] = (brightness, brightness, brightness, brightness)
    pixels.show()

def main():
    try:
        # Set maximum brightness white light
        set_white_brightness(255)  # 255 is the maximum brightness value

        # Keep the light on for 10 seconds (adjust as needed)
        time.sleep(10)

    finally:
        # Turn off NeoPixels
        pixels.fill((0, 0, 0, 0))
        pixels.show()

if __name__ == "__main__":
    main()