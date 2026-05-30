import can
import cantools
import time
import threading
import random
from flask import Flask, render_template
from flask_socketio import SocketIO

DBC_FILE = 'network.dbc'
db = cantools.database.load_file(DBC_FILE)

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading') 
bus = can.Bus(channel='vbus', interface='virtual')

# --- FAULT INJECTION FLAGS ---
fault_flags = {
    'drop_frames': False,
    'corrupt_payload': False,
    'babbling_idiot': False
}

@socketio.on('trigger_fault')
def handle_fault(data):
    """Listens for sabotage commands from the web UI"""
    fault_type = data['type']
    state = data['state']
    fault_flags[fault_type] = state
    print(f"[!] FAULT INJECTED: {fault_type.upper()} is now {state}")
@socketio.on('trigger_replay')
def handle_replay():
    """Listens for the Replay button click and runs the Ghost Car in a background thread"""
    print("[*] GHOST CAR REPLAY INITIATED")
    threading.Thread(target=execute_replay, daemon=True).start()

def execute_replay():
    """Reads the log file and injects it into the shared live bus"""
    try:
        reader = can.LogReader('sample_data.log')
        last_timestamp = None
        count = 0
        
        for msg in reader:
            if last_timestamp is not None:
                delay = msg.timestamp - last_timestamp
                if delay > 0:
                    time.sleep(delay)
            
            # Send the ghost frame directly to the live bus
            bus.send(msg)
            last_timestamp = msg.timestamp
            count += 1
            
        print(f"[*] REPLAY COMPLETE: Injected {count} historical frames.")
    except FileNotFoundError:
        print("[!] ERROR: 'sample_data.log' not found.")
    except Exception as e:
        print(f"[!] Replay Error: {e}")

# --- HARDWARE SIMULATION THREADS ---
def ecu_engine():
    msg_id = db.get_message_by_name('EngineController').frame_id
    while True:
        torque = random.randint(40, 80)
        
        # We use a bytearray so we can mutate the payload
        data = bytearray(db.encode_message('EngineController', {'EngineTorque': torque}))
        
        # FAULT 2: Corrupt Payload (Simulating EMI / Bit Flip)
        if fault_flags['corrupt_payload']:
            # XOR the first byte with FF to completely invert the data bits
            data[0] ^= 0xFF 
            
        msg = can.Message(arbitration_id=msg_id, data=data, is_extended_id=True)
        
        # FAULT 1: Frame Drop (Simulating a loose wire - 30% drop chance)
        if fault_flags['drop_frames'] and random.random() < 0.30:
            pass # Message is lost to the void
        else:
            bus.send(msg)
            
        time.sleep(0.05)

def ecu_transmission():
    msg_id = db.get_message_by_name('Transmission').frame_id
    gear = 1
    while True:
        data = db.encode_message('Transmission', {'GearPosition': gear})
        msg = can.Message(arbitration_id=msg_id, data=data, is_extended_id=True)
        bus.send(msg)
        gear = gear + 1 if gear < 5 else 1
        time.sleep(0.5)

def ecu_brakes():
    msg_id = db.get_message_by_name('Brakes').frame_id
    while True:
        pedal_pressure = random.choice([0, 0, 20, 50, 80]) 
        data = db.encode_message('Brakes', {'BrakePedal': pedal_pressure})
        msg = can.Message(arbitration_id=msg_id, data=data, is_extended_id=True)
        bus.send(msg)
        time.sleep(1.0)

def ecu_rogue_node():
    """FAULT 3: The Babbling Idiot. Floods the bus with Priority 0."""
    while True:
        if fault_flags['babbling_idiot']:
            # ID 0x000 wins ALL arbitration. No other ECU can talk.
            msg = can.Message(arbitration_id=0x000, data=[0xFF]*8, is_extended_id=False)
            try:
                bus.send(msg)
            except:
                pass
            time.sleep(0.002) # Spamming at a catastrophic 500Hz
        else:
            time.sleep(0.5) # Sleep while the fault is inactive

# --- WEBSOCKET BRIDGE ---
def network_monitor_websocket():
    rx_bus = can.Bus(channel='vbus', interface='virtual')
    while True:
        msg = rx_bus.recv(timeout=1.0)
        if msg:
            try:
                decoded = db.decode_message(msg.arbitration_id, msg.data)
                msg_name = db.get_message_by_frame_id(msg.arbitration_id).name
                socketio.emit('can_data', {
                    'time': round(msg.timestamp, 4),
                    'node': msg_name,
                    'data': decoded
                })
            except KeyError:
                # If we catch the Rogue Node's ID, it won't be in our DBC dictionary!
                if msg.arbitration_id == 0x000:
                    socketio.emit('can_data', {
                        'time': round(msg.timestamp, 4),
                        'node': 'UNKNOWN_ROGUE',
                        'data': 'CORRUPT_DATA_SPAM'
                    })

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    threading.Thread(target=ecu_engine, daemon=True).start()
    threading.Thread(target=ecu_transmission, daemon=True).start()
    threading.Thread(target=ecu_brakes, daemon=True).start()
    threading.Thread(target=ecu_rogue_node, daemon=True).start()
    threading.Thread(target=network_monitor_websocket, daemon=True).start()
    socketio.run(app, debug=False, allow_unsafe_werkzeug=True)