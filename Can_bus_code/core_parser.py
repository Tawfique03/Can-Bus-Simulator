import can
import sys

LOG_FILE = 'sample_data.log' 

def run_parser():
    print(f"Opening CAN log: {LOG_FILE}...\n")
    print("-" * 65)
    
    try:
        #Initialize the reader
        reader = can.LogReader(LOG_FILE)
        
        #Set up the loop and counter
        message_count = 0
        
        for msg in reader:
            #Professional Hex Formatting
            
            # 1. Timestamp: Force to 4 decimal places
            time_str = f"{msg.timestamp:.4f}"
            
            # 2. Arbitration ID: Format as uppercase Hex, padded to 8 characters 
            # (08X ensures Extended IDs like J1939 align perfectly)
            id_str = f"0x{msg.arbitration_id:08X}"
            
            # 3. DLC: Standard integer
            dlc_str = msg.dlc
            
            # 4. Data Payload: Iterate through the bytearray, format each byte 
            # as a 2-character Hex (02X), and join them with a space
            data_str = ' '.join(f"{byte:02X}" for byte in msg.data)
            
            # Print the cleanly aligned output
            print(f"Time: {time_str} | ID: {id_str} | DLC: {dlc_str} | Data: {data_str}")
            
            # Stop exactly at 10 iterations so we don't crash the terminal
            message_count += 1
            if message_count >= 10:
                break
                
        print("-" * 65)
        print("Parser test complete. 10 frames read successfully.")

    except FileNotFoundError:
        print(f"Error: Could not find '{LOG_FILE}'.")
        print("Please check the file name and ensure it is in the same directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_parser()