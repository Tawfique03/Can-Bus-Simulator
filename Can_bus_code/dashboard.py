import can
import cantools
import time
import threading
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation

DBC_FILE = 'network.dbc'

print("Loading Database and Initializing Network...")
db = cantools.database.load_file(DBC_FILE)

# Node A: The Engine Controller (Transmitter)
# Note: 'bustype' is updated to 'interface' to fix your deprecation warning
tx_bus = can.Bus(channel='vbus', interface='virtual')

# Node B: The Dashboard Display (Receiver)
rx_bus = can.Bus(channel='vbus', interface='virtual')

# Global arrays to hold our telemetry data for plotting
x_data, y_data = [], []
start_time = time.time()

def simulate_engine_ecu():
    """Background Thread: Simulates an engine revving up and down (Sine Wave)"""
    print("ECU Transmitter Online. Broadcasting...")
    t = 0
    while True:
        # Generate a fluctuating torque value between 20% and 80%
        torque_val = int(50 + 30 * math.sin(t))
        
        # Encode and send
        data_bytes = db.encode_message('EngineController', {'EngineTorque': torque_val})
        msg_id = db.get_message_by_name('EngineController').frame_id
        
        msg = can.Message(arbitration_id=msg_id, data=data_bytes, is_extended_id=True)
        tx_bus.send(msg)
        
        t += 0.2
        time.sleep(0.05) # Blast data at 20Hz

def update_graph(frame):
    """Main Thread: Reads from the bus and updates the Matplotlib UI"""
    # Listen to the bus for 0.1 seconds
    msg = rx_bus.recv(timeout=0.1)
    
    if msg is not None:
        try:
            # Decode the raw hex back into physical values
            decoded = db.decode_message(msg.arbitration_id, msg.data)
            
            if 'EngineTorque' in decoded:
                current_time = time.time() - start_time
                torque = decoded['EngineTorque']
                
                # Append to our graphing arrays
                x_data.append(current_time)
                y_data.append(torque)
                
                # Keep only the last 50 points so the graph scrolls cleanly
                x_plot = x_data[-50:]
                y_plot = y_data[-50:]
                
                # Draw the UI
                ax.clear()
                ax.plot(x_plot, y_plot, color='#00ffcc', linewidth=3) # Tech/Futuristic Cyan
                
                # Styling the dashboard
                fig.patch.set_facecolor('#1e1e1e')
                ax.set_facecolor('#1e1e1e')
                ax.tick_params(colors='white')
                ax.set_title("LIVE TELEMETRY: Engine Torque", color='white', fontsize=14, pad=15)
                ax.set_xlabel("Time (Seconds)", color='#aaaaaa')
                ax.set_ylabel("Torque (%)", color='#aaaaaa')
                ax.set_ylim(0, 100)
                ax.grid(True, color='#333333', linestyle='--')
                
        except KeyError:
            pass

if __name__ == "__main__":
    # 1. Boot up the Engine ECU in the background
    ecu_thread = threading.Thread(target=simulate_engine_ecu, daemon=True)
    ecu_thread.start()

    # 2. Setup the UI Window
    fig, ax = plt.subplots(figsize=(9, 5))
    
    # 3. Launch the live animation loop
    print("Launching Visual Dashboard...")
    ani = animation.FuncAnimation(fig, update_graph, interval=50, cache_frame_data=False)
    
    try:
        plt.show()
    except KeyboardInterrupt:
        pass
    finally:
        # Fixes the shutdown warning from Day 3
        tx_bus.shutdown()
        rx_bus.shutdown()
        print("Network buses safely powered down.")