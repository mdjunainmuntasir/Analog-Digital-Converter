#!/usr/bin/python3
# Md Junain Muntasir
# Date: 12 July, 2024

import time
from smbus2 import SMBus
from gpiozero import PWMLED
from math import log10, pow
from signal import signal, SIGTERM, SIGHUP, pause

# I2C address of the ADC
ADC_ADDRESS = 0x4b

# Initialize the I2C bus
bus = SMBus(1)

# Setup the LED
led = PWMLED(19)  # Use appropriate GPIO pin for the LED

# ADC and LED configuration
steps = 255
fade_factor = (steps * log10(2)) / log10(steps)

# Commands for ADS7830
ads7830_commands = [0x84, 0xC4, 0x94, 0xD4, 0xA4, 0xE4, 0xB4, 0xF4]

active = True  # Control variable for stopping the loop

def safe_exit(signum, frame):
    """Exit cleanly when a signal is received."""
    global active
    active = False
    led.off()
    exit(1)

def read_ads7830(channel):
    """Read the ADC value from the specified channel."""
    if channel < 0 or channel > 7:
        return -1
    command = ads7830_commands[channel]
    bus.write_byte(ADC_ADDRESS, command)
    value = bus.read_byte(ADC_ADDRESS)
    return value

def values(channel):
    """Generate normalized ADC values for controlling LED brightness."""
    while active:
        value = read_ads7830(channel)
        normalized_value = (pow(2, (value / fade_factor)) - 1) / steps
        yield normalized_value

def read_adc_and_control_led():
    """Set the LED source to the ADC values and control the LED brightness."""
    led.source_delay = 0.05
    led.source = values(0)  # Read from channel 0
    pause()

try:
    # Set up signal handlers for clean termination
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    # Start reading ADC values and controlling the LED
    read_adc_and_control_led()

except KeyboardInterrupt:
    pass

finally:
    # Ensure clean exit
    active = False
    led.off()
