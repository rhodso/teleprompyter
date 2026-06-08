import json
import math
import re
import tkinter as tk
from tkinter import font

# Load Config
with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)

with open("script.txt", "r", encoding="utf-8") as file:
    script_content = file.read()

# Script Parsing
def split_long_line(text, max_length):
    words = text.split()

    if not words:
        return []

    result = []
    current = words[0]

    for word in words[1:]:
        candidate = current + " " + word

        if len(candidate) <= max_length:
            current = candidate
        else:
            result.append(current)
            current = word

    result.append(current)
    return result

# Splits script into lines based on punctuation and max length
def build_script_lines(script, max_length):
    output = []
    raw_lines = script.splitlines()

    for raw_line in raw_lines:
        raw_line = raw_line.strip()

        if not raw_line:
            continue

        punctuation_chunks = re.split( r'(?<=[.,!?;:])\s+', raw_line )

        for chunk in punctuation_chunks:
            chunk = chunk.strip()

            if not chunk:
                continue

            if len(chunk) <= max_length:
                output.append(chunk)
            else:
                output.extend( split_long_line( chunk, max_length ))

    return output

script_lines = build_script_lines( script_content, config["max_char_length"] )

# Check there is something to show
if not script_lines:
    script_lines = ["No script content found."]

# Font Size Calculation
def calculate_font_size(root, lines):
    screen_width = config["screen_width"]
    screen_height = config["screen_height"]
    margin = config.get( "margin_percent", 0.05 )
    usable_width = screen_width * (1 - (margin * 2))

    # Each text block gets roughly 1/3 of the screen.
    usable_height = (screen_height / 3) * 0.8
    longest_line = max( lines, key=len )

    low = 8
    high = 300
    best = 8

    while low <= high:
        size = (low + high) // 2
        test_font = font.Font( root=root, family=config["font_family"], size=size )
        line_height = test_font.metrics( "linespace" )
        text_width = test_font.measure( longest_line )
        wrapped_lines = max( 1, math.ceil( text_width / usable_width ))
        total_height = ( wrapped_lines * line_height )

        if total_height <= usable_height:
            best = size
            low = size + 1
        else:
            high = size - 1
    return best

# Teleprompter
class Teleprompter:
    def __init__(self, root, lines):
        
		# Code generated from some online tool
        # No touchy

        self.root = root
        self.lines = lines
        self.index = 0

        self.root.title( "Teleprompter" )
        self.root.geometry( f"{config['screen_width']}x{config['screen_height']}" )
        self.root.configure( bg=config["background_color"] )
        self.root.attributes( "-fullscreen", True)

        margin = config.get( "margin_percent", 0.05 )
        wrap_length = int( config["screen_width"] * (1 - margin * 2) )
        calculated_size = calculate_font_size( root, lines )
        # print( f"Calculated font size: {calculated_size}") # Debug

        self.text_font = font.Font(
            family=config["font_family"],
            size=calculated_size
        )

        self.top_label = tk.Label(
            root,
            bg=config["background_color"],
            fg=config["font_color"],
            font=self.text_font,
            wraplength=wrap_length,
            justify="center"
        )

        self.current_label = tk.Label(
            root,
            bg=config["background_color"],
            fg=config["font_color"],
            font=self.text_font,
            wraplength=wrap_length,
            justify="center"
        )

        self.bottom_label = tk.Label(
            root,
            bg=config["background_color"],
            fg=config["font_color"],
            font=self.text_font,
            wraplength=wrap_length,
            justify="center"
        )

        self.top_label.pack( expand=True, fill="both" )
        self.current_label.pack( expand=True, fill="both" )
        self.bottom_label.pack( expand=True, fill="both" )

        # Controls
        root.bind( "<Button-1>", self.next_line )
        root.bind( "<Button-3>", self.previous_line )
        root.bind( "<Right>", self.next_line )
        root.bind( "<Left>", self.previous_line )
        root.bind( "<space>", self.next_line )
        root.bind( "<BackSpace>", self.previous_line )
        root.bind( "<Escape>", self.exit_program )

        self.refresh()

	# Glad that's over
    # UI sucks even if simple

    def get_line(self, index):
        if 0 <= index < len(self.lines):
            return self.lines[index]
        return ""

    def refresh(self):
        self.top_label.config( text=self.get_line( self.index - 1 ))
        self.current_label.config( text=self.get_line( self.index ))
        self.bottom_label.config( text=self.get_line( self.index + 1 ))
        self.root.title( f"Teleprompter " f"({self.index + 1}/{len(self.lines)})" )

    def next_line(self, event=None):
        if self.index < len(self.lines) - 1:
            self.index += 1
            self.refresh()

    def previous_line(self, event=None):
        if self.index > 0:
            self.index -= 1
            self.refresh()

    def exit_program(self, event=None):
        self.root.destroy()

# Run
root = tk.Tk()
app = Teleprompter( root, script_lines )
root.mainloop()

