import os
import time
import datetime
from flask import Flask, render_template, request, jsonify
import gpiod
from gpiod.line import Direction, Edge, Bias, Value

app = Flask(__name__)

# ==========================================================
# --- ECHANICAL & WORKSPACE RANGE CONFIGURATION --------
# ==========================================================
MICROSTEPS_PER_REV = 1600
MECHANICAL_LEAD_MM = 5.0    # SFU1605 Lead Screw = 5.0 mm travel per revolution
TOTAL_STROKE_MM = 500.0     # CBX1605 total slide rail length

# Symmetric Boundaries (-250.0 mm to +250.0 mm)
MIN_SAFE_TRAVEL_MM = -(TOTAL_STROKE_MM / 2.0)
MAX_SAFE_TRAVEL_MM = (TOTAL_STROKE_MM / 2.0)

STEPS_PER_MM = MICROSTEPS_PER_REV / MECHANICAL_LEAD_MM

FAST_DELAY = 0.0003   # Cruising speed interval (~3333 steps/sec)
SLOW_DELAY = 0.0020   # Fine-touch calibration crawl speed
START_DELAY = 0.0015  # Soft-start launch delay
RAMP_STEPS = 200      # Acceleration ramp profile envelope

# --- LINUX HARDWARE GPIO PIN MAP -----------------------
CHIP_PATH = "/dev/gpiochip0"  # Update to "/dev/gpiochip4" for Raspberry Pi 5
SWITCH_LINE = 27              # Limit switch mounted at the extreme Left end
STEP_PIN = 12
DIR_PIN = 16

line_config = {
    SWITCH_LINE: gpiod.LineSettings(direction=Direction.INPUT, bias=Bias.PULL_UP, edge_detection=Edge.BOTH),
    STEP_PIN: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.INACTIVE),
    DIR_PIN:  gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.INACTIVE)
}

# Request lines globally to persist state across asynchronous web requests
gpio_request = gpiod.request_lines(CHIP_PATH, consumer="flask-linear-calibrated", config=line_config)

# Global runtime state tracking variables
current_position_mm = 0.0
is_moving = False
is_calibrated = False  # Blocks target movements until system has homed safely

# --- SIMULTANEOUS STEPPING ENGINE ----------------------
def set_direction(forward: bool):
    gpio_request.set_value(DIR_PIN, Value.ACTIVE if forward else Value.INACTIVE)

def pulse_step(delay_sec: float):
    gpio_request.set_value(STEP_PIN, Value.ACTIVE)
    time.sleep(0.000005) # 5 microsecond gate latch high hold
    gpio_request.set_value(STEP_PIN, Value.INACTIVE)
    time.sleep(delay_sec)

def move_to_coordinate(target_mm: float):
    global current_position_mm, is_moving
    
    if not (MIN_SAFE_TRAVEL_MM <= target_mm <= MAX_SAFE_TRAVEL_MM):
        raise ValueError("Target outside structural safety safety window")

    is_moving = True
    delta_mm = target_mm - current_position_mm
    
    if delta_mm == 0:
        is_moving = False
        return

    steps_to_move = int(round(abs(delta_mm) * STEPS_PER_MM))
    forward = delta_mm > 0
    
    set_direction(forward)
    local_ramp = min(RAMP_STEPS, steps_to_move // 2)

    for i in range(steps_to_move):
        if i < local_ramp:
            progress = i / local_ramp
            current_delay = START_DELAY - ((START_DELAY - FAST_DELAY) * progress)
        elif i > (steps_to_move - local_ramp):
            progress = (steps_to_move - i) / local_ramp
            current_delay = START_DELAY - ((START_DELAY - FAST_DELAY) * progress)
        else:
            current_delay = FAST_DELAY

        pulse_step(current_delay)

    current_position_mm = target_mm
    is_moving = False

# --- CALIBRATION AUTOMATION SEQUENCING -----------------
def execute_calibration_sequence():
    global current_position_mm, is_moving, is_calibrated
    is_moving = True
    is_calibrated = False
    
    # Safety Check: If resting hard directly on the switch at boot, pull away first
    if gpio_request.get_value(SWITCH_LINE) == Value.ACTIVE:
        print("imit switch active on boot. Clearing clearance zone...")
        set_direction(forward=True) # Move right
        for _ in range(MICROSTEPS_PER_REV * 2): # Pull away 2 revolutions
            pulse_step(FAST_DELAY)
        time.sleep(0.5)

    # PHASE 1: Rapid Homing Seek (Move Left until contact)
    print("hase 1: Seeking limit switch boundary...")
    set_direction(forward=False)
    while gpio_request.get_value(SWITCH_LINE) != Value.ACTIVE:
        pulse_step(FAST_DELAY)
        if gpio_request.wait_edge_events(timeout=datetime.timedelta(microseconds=5)):
            gpio_request.read_edge_events()
            
    time.sleep(0.4)

    # PHASE 2: Clear Switch zone (Move right slightly)
    print("hase 2: Clearing physical latch saturation...")
    set_direction(forward=True)
    for _ in range(MICROSTEPS_PER_REV): # Move right 1 full rotation
        pulse_step(FAST_DELAY)
    time.sleep(0.4)

    # PHASE 3: High-Precision Index Crawl (Move left very slowly)
    print("Phase 3: Crawling slowly for accurate zero tracking point...")
    set_direction(forward=False)
    while gpio_request.get_value(SWITCH_LINE) != Value.ACTIVE:
        pulse_step(SLOW_DELAY)
        if gpio_request.wait_edge_events(timeout=datetime.timedelta(microseconds=5)):
            gpio_request.read_edge_events()

    # Hardware Boundary Found! This physical location is absolute -250.0mm
    print("Hardware home detected.")
    time.sleep(0.5)
    
    # PHASE 4: Center Displacement Shift Math
    # Calculate steps required to travel exactly to the midpoint of the rail
    center_offset_distance_mm = TOTAL_STROKE_MM / 2.0  # 250.0 mm
    offset_steps = int(round(center_offset_distance_mm * STEPS_PER_MM))
    
    print(f"Phase 4: Advancing {center_offset_distance_mm}mm to center coordinate matrix...")
    set_direction(forward=True) # Shift away from limit switch
    
    # Move to the midpoint utilizing our acceleration profiles
    local_ramp = min(RAMP_STEPS, offset_steps // 2)
    for i in range(offset_steps):
        if i < local_ramp:
            progress = i / local_ramp
            current_delay = START_DELAY - ((START_DELAY - FAST_DELAY) * progress)
        elif i > (offset_steps - local_ramp):
            progress = (offset_steps - i) / local_ramp
            current_delay = START_DELAY - ((START_DELAY - FAST_DELAY) * progress)
        else:
            current_delay = FAST_DELAY
        pulse_step(current_delay)

    # Re-index state variables to true symmetric origin center coordinate point
    current_position_mm = 0.0
    is_moving = False
    is_calibrated = True
    print("Calibration complete. Symmetric workspace established.")

# --- WEB CONTROLLERS -----------------------------------
@app.route('/')
def home():
    return render_template('code_for.html', position=current_position_mm, min_travel=MIN_SAFE_TRAVEL_MM, max_travel=MAX_SAFE_TRAVEL_MM, calibrated=is_calibrated)

@app.route('/calibrate', methods=['POST'])
def handle_calibration():
    global is_moving
    if is_moving:
        return jsonify({"error": "Motor is busy processing an active motion path"}), 409
    
    print("Remote command received: Init full hardware axis homing alignment...")
    execute_calibration_sequence()
    return jsonify({"position": current_position_mm, "status": "Calibration successfully updated and validated"})

@app.route('/move', methods=['POST'])
def handle_move():
    global current_position_mm, is_moving, is_calibrated
    
    if not is_calibrated:
        return jsonify({"error": "Axis uncalibrated. Run the Homing Sequence first to map boundaries safely."}), 403
        
    if is_moving:
        return jsonify({"error": "Motor is busy executing another profile"}), 409
        
    data = request.get_json() or {}
    try:
        if 'jog' in data:
            direction = data.get('jog')
            step_size = float(data.get('step_size', 5.0))
            target = current_position_mm + (step_size if direction == 'forward' else -step_size)
        else:
            target = float(data.get('target', 0.0))
            
        if not (MIN_SAFE_TRAVEL_MM <= target <= MAX_SAFE_TRAVEL_MM):
            return jsonify({"error": f"Target outside structural safety window ({MIN_SAFE_TRAVEL_MM} to {MAX_SAFE_TRAVEL_MM}mm)"}), 400
            
        move_to_coordinate(target)
        return jsonify({"position": current_position_mm, "status": "Coordinates Updated"})
        
    except ValueError:
        return jsonify({"error": "Invalid numerical format specified"}), 400

import atexit
@atexit.register
def cleanup():
    gpio_request.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
