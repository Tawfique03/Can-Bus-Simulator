import can
import cantools
import time

DBC_FILE = 'network.dbc'

def run_simulator():
    print(f"Loading DBC database: {DBC_FILE}...")
    db = cantools.database.load_file(DBC_FILE)
    
    # 1. Initialize a Virtual CAN Bus in RAM
    # This simulates plugging a physical wire into an OBD-II port
    bus = can.Bus('vbus', bustype='virtual')
    
    print("-" * 65)
    print("Starting Engine ECU Simulation (Transmitting Live Data)...")
    print("Press Ctrl+C to stop.")
    print("-" * 65)
    
    try:
        # Simulate an engine revving up from 50% to 65% torque
        for torque_val in range(50, 66):
            
            # 2. ENCODE: Translate human value to raw bytes using our dictionary
            data_bytes = db.encode_message('EngineController', {'EngineTorque': torque_val})
            
            # 3. Get the correct 29-bit Extended ID for the EngineController
            msg_id = db.get_message_by_name('EngineController').frame_id
            
            # 4. Create the hardware-level CAN frame
            msg = can.Message(
                arbitration_id=msg_id, 
                data=data_bytes, 
                is_extended_id=True # Remember Day 2: We must flag this as a 29-bit ID!
            )
            
            # 5. Transmit to the bus
            bus.send(msg)
            
            # Format the hex output nicely for the console so we can see what we sent
            hex_payload = ' '.join(f"{b:02X}" for b in data_bytes)
            print(f"Simulating Torque: {torque_val}% | Broadcasted Frame -> ID: 0x{msg_id:08X} Data: [{hex_payload}]")
            
            # Wait 500ms before sending the next frame (simulating a 2Hz broadcast rate)
            time.sleep(0.5)
            
        print("\nSimulation complete. Engine shutdown.")

    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")

if __name__ == "__main__":
    run_simulator()