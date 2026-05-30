import can
import cantools
import time
import threading
import random

DBC_FILE = 'network.dbc'

print(f"Loading DBC database: {DBC_FILE}...")
db = cantools.database.load_file(DBC_FILE)

# Initialize the shared virtual bus
bus = can.Bus(channel='vbus', interface='virtual')

def ecu_engine():
    """Simulates the Engine Control Unit (High Priority, Fast Broadcast)"""
    msg_id = db.get_message_by_name('EngineController').frame_id
    while True:
        # Simulate torque fluctuating between 40% and 80%
        torque = random.randint(40, 80)
        data = db.encode_message('EngineController', {'EngineTorque': torque})
        
        msg = can.Message(arbitration_id=msg_id, data=data, is_extended_id=True)
        bus.send(msg)
        
        # Fast broadcast: 50ms (20Hz)
        time.sleep(0.05)

def ecu_transmission():
    """Simulates the Transmission Control Unit (Medium Priority)"""
    msg_id = db.get_message_by_name('Transmission').frame_id
    gear = 1
    while True:
        # Shift gears up to 5, then reset
        data = db.encode_message('Transmission', {'GearPosition': gear})
        msg = can.Message(arbitration_id=msg_id, data=data, is_extended_id=True)
        bus.send(msg)
        
        gear = gear + 1 if gear < 5 else 1
        
        # Medium broadcast: 500ms (2Hz)
        time.sleep(0.5)

def ecu_brakes():
    """Simulates the Anti-lock Braking System (High Priority, Event-Driven)"""
    msg_id = db.get_message_by_name('Brakes').frame_id
    while True:
        # Simulate someone tapping the brakes periodically
        pedal_pressure = random.choice([0, 0, 20, 50, 80]) 
        data = db.encode_message('Brakes', {'BrakePedal': pedal_pressure})
        
        msg = can.Message(arbitration_id=msg_id, data=data, is_extended_id=True)
        bus.send(msg)
        
        # Slow broadcast: 1000ms (1Hz)
        time.sleep(1.0)

def network_monitor():
    """Acts as the Diagnostic Tool listening to the chaotic bus"""
    print("-" * 65)
    print("Multi-Node Network Online. Monitoring Bus Traffic...")
    print("Press Ctrl+C to stop.")
    print("-" * 65)
    
    # We use a secondary bus connection to "listen" without interrupting
    rx_bus = can.Bus(channel='vbus', interface='virtual')
    
    while True:
        msg = rx_bus.recv(timeout=1.0)
        if msg:
            try:
                decoded = db.decode_message(msg.arbitration_id, msg.data)
                msg_name = db.get_message_by_frame_id(msg.arbitration_id).name
                
                # Format the output with fixed spacing so it looks like a real terminal
                time_str = f"{msg.timestamp:.4f}"
                print(f"[{time_str}] {msg_name:<18} -> {decoded}")
            except KeyError:
                pass

if __name__ == "__main__":
    try:
        # 1. Spin up the hardware nodes in the background
        threading.Thread(target=ecu_engine, daemon=True).start()
        threading.Thread(target=ecu_transmission, daemon=True).start()
        threading.Thread(target=ecu_brakes, daemon=True).start()
        
        # 2. Run the monitor in the main thread
        network_monitor()
        
    except KeyboardInterrupt:
        print("\nSimulation stopped. Shutting down nodes...")
        bus.shutdown()  