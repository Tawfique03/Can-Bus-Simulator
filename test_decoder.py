import cantools

def test_engine_torque_decoding():
    """Asserts that a known raw hex payload correctly translates to 50% Torque"""
    
    # 1. Load the dictionary
    db = cantools.database.load_file('network.dbc')
    
    # 2. This is the exact raw data we expect when Torque is 50%
    # Hex: AF 00 00 00 00 00 00 00
    raw_payload = bytearray([0xAF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    
    # 3. The Extended ID for the EngineController
    msg_id = 2364539904 
    
    # 4. Decode it
    decoded = db.decode_message(msg_id, raw_payload)
    
    # 5. The Assertion
    assert decoded['EngineTorque'] == 50, f"Expected 50, but got {decoded['EngineTorque']}"

def test_brake_pedal_decoding():
    """Asserts that a known raw hex payload correctly translates to 80% Brake Pressure"""
    db = cantools.database.load_file('network.dbc')
    
    # Hex: C8 00 00 00 00 00 00 00
    raw_payload = bytearray([0xC8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    msg_id = 2364539136 
    
    decoded = db.decode_message(msg_id, raw_payload)
    assert decoded['BrakePedal'] == 80.0, f"Expected 80.0, but got {decoded['BrakePedal']}"