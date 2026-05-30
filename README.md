# 🚗 CAN Bus Network Simulator & Diagnostics Suite

A software-based Controller Area Network (CAN) simulation framework built in Python. Instead of relying on expensive hardware interfaces (like Vector tools or physical OBD-II adapters), this project emulates a multi-node automotive network entirely in software. It bridges the gap between raw hardware-level hex payloads and human-readable engineering telemetry.

> **Why I built this:** Standard communication protocols (UART, I2C, SPI) are great for simple sensor integration, but modern vehicles require robust, fault-tolerant, multi-drop networks. I wanted to understand how physical CAN arbitration works, how proprietary `.dbc` files translate raw binary data into physical values, and how diagnostic tools handle catastrophic network failures. 

## ✨ Core Features

### 1. Multi-Node Asynchronous Simulation
The core engine spins up separate Python threads to act as independent hardware modules (Engine ECU, Transmission Control, ABS). These nodes continuously broadcast data onto a shared virtual bus. Because they run asynchronously, they frequently try to transmit at the exact same millisecond, forcing the underlying `python-can` interface to handle real hardware arbitration (CSMA/CD+AMP) organically.

### 2. Database CAN (.dbc) Decoding Engine
Raw automotive data is meaningless without a dictionary. This suite uses the `cantools` library to load standard `.dbc` files, instantly applying the correct bit-masks, scales, and offsets to convert 29-bit Extended Hex IDs into physical engineering units (e.g., Engine Torque %, Gear Position).

### 3. WebSockets Telemetry Dashboard
A local Flask server acts as the diagnostic listener. It catches decoded network traffic and pipes it asynchronously via WebSockets to a futuristic, glassmorphic UI. This provides live gauge updates and a continuous terminal trace without blocking the hardware simulation loops.

### 4. 💥 The Chaos Engine (Fault Injection)
A network simulator is only useful if you can break it. The dashboard includes a dedicated "Sabotage" panel to test fault tolerance:
* **Frame Drop (30%):** Simulates physical wire degradation by randomly destroying packets before transmission, visualizing packet loss.
* **EMI Simulation (Bit Flip):** XORs the binary payload to intentionally corrupt data, forcing the decoder to handle garbage inputs.
* **The "Babbling Idiot" (DoS Attack):** Floods the network with priority `0x000` messages. Because CAN arbitration favors the lower ID, this completely starves the Engine and Brake ECUs of bandwidth, causing a total network freeze.

### 5. Ghost Car (Log Replay)
Allows for temporal log replay. The system parses historical `.log` files (from real CSS Electronics drive data), calculates the precise microsecond timestamps, and injects that historical traffic back onto the live virtual bus, mixing ghost data with the live synthetic ECUs.

## 🛠️ Tech Stack & Architecture
* **Backend Engine:** Python 3.11
* **Physical Layer Emulation:** `python-can` (Virtual interface)
* **Data Translation:** `cantools` (.dbc file parsing)
* **Web Server & Async Streaming:** `Flask`, `Flask-SocketIO` (WebSockets)
* **Frontend:** HTML5, CSS3, Vanilla JS
* **Validation:** `pytest` (Automated decoding assertions)

## 🚀 Getting Started

### Prerequisites
You need Python 3.8+ installed. All network emulation runs on local memory, so no physical CAN hardware (like a PCAN or Kvaser) is required.

### Installation
```bash
# 1. Clone the repository
git clone [https://github.com/yourusername/can-bus-simulator.git](https://github.com/yourusername/can-bus-simulator.git)
cd can-bus-simulator

# 2. (Optional but recommended) Set up a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install the required libraries
pip install python-can cantools flask flask-socketio pytest
