import can
import time

LOG_FILE = 'sample_data.log'

def run_replay():
    print("-" * 50)
    print(f"INITIALIZING GHOST CAR REPLAY: {LOG_FILE}")
    print("-" * 50)
    
    try:
        # 1. Connect to our existing live network
        bus = can.Bus(channel='vbus', interface='virtual')
        
        # 2. Open the historical log file
        reader = can.LogReader(LOG_FILE)
        
        last_timestamp = None
        count = 0
        
        print("Injecting historical frames onto live bus...")
        
        for msg in reader:
            # 3. Calculate the exact real-world delay between historical frames
            if last_timestamp is not None:
                delay = msg.timestamp - last_timestamp
                if delay > 0:
                    time.sleep(delay)
            
            # 4. Transmit the historical message as if it's happening right now
            bus.send(msg)
            
            last_timestamp = msg.timestamp
            count += 1
            
            # Print a clean terminal output showing the injection
            print(f"[INJECTED] ID: 0x{msg.arbitration_id:08X} | Data: {' '.join(f'{b:02X}' for b in msg.data)}")
            
        print("-" * 50)
        print(f"REPLAY COMPLETE. {count} frames injected successfully.")

    except FileNotFoundError:
        print(f"Error: Could not find '{LOG_FILE}'.")
    except Exception as e:
        print(f"System Error: {e}")

if __name__ == "__main__":
    run_replay()