import can
import cantools

LOG_FILE = 'sample_data.log'
DBC_FILE = 'network.dbc'

def run_decoder():
    print(f"Loading DBC database: {DBC_FILE}...")
    
    # 1. Load the dictionary into memory
    db = cantools.database.load_file(DBC_FILE)
    print("DBC loaded successfully!\n")
    print("-" * 65)
    
    # 2. Open the log file just like yesterday
    reader = can.LogReader(LOG_FILE)
    
    for msg in reader:
        try:
            # 3. THE MAGIC: Tell cantools to decode the payload based on the ID
            decoded_data = db.decode_message(msg.arbitration_id, msg.data)
            
            # 4. Get the human-readable name of the message (e.g., "EngineController")
            msg_name = db.get_message_by_frame_id(msg.arbitration_id).name
            
            time_str = f"{msg.timestamp:.4f}"
            
            # Print the final translated data
            print(f"[{time_str}] {msg_name} -> {decoded_data}")
            
        except KeyError:
            # If an ID is in the log but NOT in our DBC file, cantools throws a KeyError.
            # We just ignore it and move to the next frame.
            pass

if __name__ == "__main__":
    run_decoder()