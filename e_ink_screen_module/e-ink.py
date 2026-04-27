from micropython import const
from machine import Pin, SPI
import framebuf
import time

# =========================================================
# 1. E-PAPER DRIVER CLASS (Merged to prevent import errors)
# =========================================================
EPD_WIDTH  = const(176)
EPD_HEIGHT = const(264)

PANEL_SETTING               = const(0x00)
POWER_SETTING               = const(0x01)
POWER_ON                    = const(0x04)
BOOSTER_SOFT_START          = const(0x06)
DEEP_SLEEP                  = const(0x07)
DATA_START_TRANSMISSION_1   = const(0x10)
DISPLAY_REFRESH             = const(0x12)
DATA_START_TRANSMISSION_2   = const(0x13)
PARTIAL_DISPLAY_REFRESH     = const(0x16)
LUT_FOR_VCOM                = const(0x20)
LUT_WHITE_TO_WHITE          = const(0x21)
LUT_BLACK_TO_WHITE          = const(0x22)
LUT_WHITE_TO_BLACK          = const(0x23)
LUT_BLACK_TO_BLACK          = const(0x24)
PLL_CONTROL                 = const(0x30)
VCM_DC_SETTING_REGISTER     = const(0x82)
POWER_OPTIMIZATION          = const(0xF8)

BUSY = const(0)

class EPD:
    def __init__(self, spi, cs, dc, rst, busy):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.busy = busy
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.busy.init(self.busy.IN)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    LUT_VCOM_DC = bytearray(b'\x00\x00\x00\x0F\x0F\x00\x00\x05\x00\x32\x32\x00\x00\x02\x00\x0F\x0F\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    LUT_WW      = bytearray(b'\x50\x0F\x0F\x00\x00\x05\x60\x32\x32\x00\x00\x02\xA0\x0F\x0F\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    LUT_BW      = bytearray(b'\x50\x0F\x0F\x00\x00\x05\x60\x32\x32\x00\x00\x02\xA0\x0F\x0F\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    LUT_BB      = bytearray(b'\xA0\x0F\x0F\x00\x00\x05\x60\x32\x32\x00\x00\x02\x50\x0F\x0F\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    LUT_WB      = LUT_BB
    
    def _command(self, command, data=None):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([command]))
        self.cs(1)
        if data is not None:
            self._data(data)

    def _data(self, data):
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)

    def init(self):
        self.reset()
        self._command(POWER_SETTING, b'\x03\x00\x2B\x2B\x09')
        self._command(BOOSTER_SOFT_START, b'\x07\x07\x17')
        self._command(POWER_OPTIMIZATION, b'\x60\xA5')
        self._command(POWER_OPTIMIZATION, b'\x89\xA5')
        self._command(POWER_OPTIMIZATION, b'\x90\x00')
        self._command(POWER_OPTIMIZATION, b'\x93\x2A')
        self._command(POWER_OPTIMIZATION, b'\xA0\xA5')
        self._command(POWER_OPTIMIZATION, b'\xA1\x00')
        self._command(POWER_OPTIMIZATION, b'\x73\x41')
        self._command(PARTIAL_DISPLAY_REFRESH, b'\x00')
        self._command(POWER_ON)
        self.wait_until_idle()
        self._command(PANEL_SETTING, b'\xAF')
        self._command(PLL_CONTROL, b'\x3A')
        self._command(VCM_DC_SETTING_REGISTER, b'\x12')
        time.sleep_ms(2)
        self.set_lut()

    def wait_until_idle(self):
        while self.busy.value() == BUSY:
            time.sleep_ms(100)

    def reset(self):
        self.rst(0)
        time.sleep_ms(200)
        self.rst(1)
        time.sleep_ms(200)

    def set_lut(self):
        self._command(LUT_FOR_VCOM, self.LUT_VCOM_DC)
        self._command(LUT_WHITE_TO_WHITE, self.LUT_WW)
        self._command(LUT_BLACK_TO_WHITE, self.LUT_BW)
        self._command(LUT_WHITE_TO_BLACK, self.LUT_BB)
        self._command(LUT_BLACK_TO_BLACK, self.LUT_WB)

    def display_frame(self, frame_buffer):
        if (frame_buffer != None):
            self._command(DATA_START_TRANSMISSION_1)
            time.sleep_ms(2)
            for i in range(0, self.width * self.height // 8):
                self._data(bytearray([0xFF]))
            time.sleep_ms(2)
            self._command(DATA_START_TRANSMISSION_2)
            time.sleep_ms(2)
            for i in range(0, self.width * self.height // 8):
                self._data(bytearray([frame_buffer[i]]))
            time.sleep_ms(2)
            self._command(DISPLAY_REFRESH)
            self.wait_until_idle()

    def sleep(self):
        self._command(DEEP_SLEEP, b'\xA5')


# =========================================================
# 2. HARDWARE SETUP
# =========================================================
print("Setting up hardware...")

# SPI and E-Paper Pins (Pico example)
spi = SPI(0, baudrate=20000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19))

# E-Paper Control Pins
cs = Pin(17)    # EPD_CS
dc = Pin(20)    # EPD_DC
rst = Pin(21)   # EPD_RST
busy = Pin(22)  # EPD_BUSY

# Initialize the display object
epd = EPD(spi, cs, dc, rst, busy)

# Framebuffer Setup
width = epd.width   
height = epd.height 
buffer = bytearray(width * height // 8) 
fb = framebuf.FrameBuffer(buffer, width, height, framebuf.MONO_HLSB)

# Button Pins (Connected to Ground when pressed)
btn_up = Pin(2, Pin.IN, Pin.PULL_UP)
btn_down = Pin(3, Pin.IN, Pin.PULL_UP)
btn_left = Pin(4, Pin.IN, Pin.PULL_UP)
btn_right = Pin(5, Pin.IN, Pin.PULL_UP)

# =========================================================
# 3. DRAWING FUNCTION
# =========================================================
def draw_board(fb, cursor_x, cursor_y):
    SQUARE_SIZE = 22
    fb.fill(1) # Wipe background to White (1)
    
    # Draw the 8x8 checkerboard pattern
    for row in range(8):
        for col in range(8):
            x = col * SQUARE_SIZE
            y = row * SQUARE_SIZE
            
            # Alternating colors: If row+col is odd, fill with Black (0)
            if (row + col) % 2 == 1:
                fb.fill_rect(x, y, SQUARE_SIZE, SQUARE_SIZE, 0)
            
            # Draw a black border around EVERY square
            fb.rect(x, y, SQUARE_SIZE, SQUARE_SIZE, 0)

    # Draw the Selection Cursor (Thick double-lined box)
    cx = cursor_x * SQUARE_SIZE
    cy = cursor_y * SQUARE_SIZE
    fb.rect(cx, cy, SQUARE_SIZE, SQUARE_SIZE, 1)       
    fb.rect(cx+1, cy+1, SQUARE_SIZE-2, SQUARE_SIZE-2, 0) 
    fb.rect(cx+2, cy+2, SQUARE_SIZE-4, SQUARE_SIZE-4, 1) 
    fb.rect(cx+3, cy+3, SQUARE_SIZE-6, SQUARE_SIZE-6, 0) 

    # Draw the Bottom UI Area
    chess_col = chr(65 + cursor_x) # 65 is 'A' in ASCII
    chess_row = 8 - cursor_y
    
    fb.text("MICROPYTHON CHESS", 15, 190, 0)
    fb.hline(10, 205, 156, 0) 
    fb.text(f"Cursor: [ {chess_col}{chess_row} ]", 15, 215, 0)
    fb.text("Waiting for move...", 15, 235, 0)

# =========================================================
# 4. GAME LOOP & LOGIC
# =========================================================
cursor_x = 0
cursor_y = 0
last_input_time = time.ticks_ms()
pending_update = True 

print("Starting game loop! Press the buttons to move.")

while True:
    input_detected = False
    
    # Check buttons (0 means it is being pressed down)
    if btn_up.value() == 0:
        cursor_y = max(0, cursor_y - 1)
        input_detected = True
    elif btn_down.value() == 0:
        cursor_y = min(7, cursor_y + 1)
        input_detected = True
    elif btn_left.value() == 0:
        cursor_x = max(0, cursor_x - 1)
        input_detected = True
    elif btn_right.value() == 0:
        cursor_x = min(7, cursor_x + 1)
        input_detected = True
        
    # If a button was pressed, reset the timer and flag an update
    if input_detected:
        last_input_time = time.ticks_ms()
        pending_update = True
        time.sleep_ms(200) 
        
    # Check if we need to update AND if the user has paused for 1.5 seconds
    current_time = time.ticks_ms()
    time_since_last_press = time.ticks_diff(current_time, last_input_time)
    
    if pending_update and time_since_last_press > 1500:
        print(f"User paused. Updating screen to {chr(65+cursor_x)}{8-cursor_y}...")
        
        draw_board(fb, cursor_x, cursor_y)
        
        # Wake up the display, push the image, and put it back to sleep
        epd.init() 
        epd.display_frame(buffer)
        epd.sleep()
        
        pending_update = False 
        print("Ready for next move.")
        
    # Small delay to keep the loop from hogging the CPU
    time.sleep_ms(50)