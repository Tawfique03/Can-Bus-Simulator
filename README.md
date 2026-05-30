<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
        color: #24292e;
        line-height: 1.5;
        margin: 0;
        padding: 40px;
        background-color: #ffffff;
    }
    h1, h2, h3 {
        color: #24292e;
        margin-top: 24px;
        margin-bottom: 16px;
        font-weight: 600;
        line-height: 1.25;
    }
    h1 { font-size: 2em; padding-bottom: 0.3em; border-bottom: 1px solid #eaecef; }
    h2 { font-size: 1.5em; padding-bottom: 0.3em; border-bottom: 1px solid #eaecef; }
    h3 { font-size: 1.25em; }
    p, blockquote, ul, ol, dl, table, pre, details {
        margin-top: 0;
        margin-bottom: 16px;
    }
    code {
        padding: 0.2em 0.4em;
        margin: 0;
        font-size: 85%;
        background-color: rgba(27,31,35,0.05);
        border-radius: 3px;
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    }
    pre {
        padding: 16px;
        overflow: auto;
        font-size: 85%;
        line-height: 1.45;
        background-color: #f6f8fa;
        border-radius: 3px;
        word-wrap: normal;
    }
    pre code {
        display: inline;
        max-width: auto;
        padding: 0;
        margin: 0;
        overflow: visible;
        line-height: inherit;
        word-wrap: normal;
        background-color: transparent;
        border: 0;
    }
    blockquote {
        padding: 0 1em;
        color: #6a737d;
        border-left: 0.25em solid #dfe2e5;
    }
    ul, ol {
        padding-left: 2em;
    }
    li {
        word-wrap: break-all;
    }
    .highlight-note {
        background-color: #f0f8ff;
        border-left: 4px solid #0366d6;
        padding: 15px;
        margin: 20px 0;
    }
</style>
</head>
<body>
    <h1>🚗 CAN Bus Network Simulator & Diagnostics Suite</h1>
    
    <p>A software-based Controller Area Network (CAN) simulation framework built in Python. Instead of relying on expensive hardware interfaces (like Vector tools or physical OBD-II adapters), this project emulates a multi-node automotive network entirely in software. It bridges the gap between raw hardware-level hex payloads and human-readable engineering telemetry.</p>
    
    <div class="highlight-note">
        <strong>Why I built this:</strong> Standard communication protocols (UART, I2C, SPI) are great for simple sensor integration, but modern vehicles require robust, fault-tolerant, multi-drop networks. I wanted to understand how physical CAN arbitration works, how proprietary `.dbc` files translate raw binary data into physical values, and how diagnostic tools handle catastrophic network failures. 
    </div>

    <h2>✨ Core Features</h2>

    <h3>1. Multi-Node Asynchronous Simulation</h3>
    <p>The core engine spins up separate Python threads to act as independent hardware modules (Engine ECU, Transmission Control, ABS). These nodes continuously broadcast data onto a shared virtual bus. Because they run asynchronously, they frequently try to transmit at the exact same millisecond, forcing the underlying `python-can` interface to handle real hardware arbitration (CSMA/CD+AMP) organically.</p>

    <h3>2. Database CAN (.dbc) Decoding Engine</h3>
    <p>Raw automotive data is meaningless without a dictionary. This suite uses the <code>cantools</code> library to load standard `.dbc` files, instantly applying the correct bit-masks, scales, and offsets to convert 29-bit Extended Hex IDs into physical engineering units (e.g., Engine Torque %, Gear Position).</p>

    <h3>3. WebSockets Telemetry Dashboard</h3>
    <p>A local Flask server acts as the diagnostic listener. It catches decoded network traffic and pipes it asynchronously via WebSockets to a futuristic, glassmorphic UI. This provides live gauge updates and a continuous terminal trace without blocking the hardware simulation loops.</p>

    <h3>4. 💥 The Chaos Engine (Fault Injection)</h3>
    <p>A network simulator is only useful if you can break it. The dashboard includes a dedicated "Sabotage" panel to test fault tolerance:</p>
    <ul>
        <li><strong>Frame Drop (30%):</strong> Simulates physical wire degradation by randomly destroying packets before transmission, visualizing packet loss.</li>
        <li><strong>EMI Simulation (Bit Flip):</strong> XORs the binary payload to intentionally corrupt data, forcing the decoder to handle garbage inputs.</li>
        <li><strong>The "Babbling Idiot" (DoS Attack):</strong> Floods the network with priority <code>0x000</code> messages. Because CAN arbitration favors the lower ID, this completely starves the Engine and Brake ECUs of bandwidth, causing a total network freeze.</li>
    </ul>

    <h3>5. Ghost Car (Log Replay)</h3>
    <p>Allows for temporal log replay. The system parses historical <code>.log</code> files (from real CSS Electronics drive data), calculates the precise microsecond timestamps, and injects that historical traffic back onto the live virtual bus, mixing ghost data with the live synthetic ECUs.</p>

    <h2>🛠️ Tech Stack & Architecture</h2>
    <ul>
        <li><strong>Backend Engine:</strong> Python 3.11</li>
        <li><strong>Physical Layer Emulation:</strong> <code>python-can</code> (Virtual interface)</li>
        <li><strong>Data Translation:</strong> <code>cantools</code> (.dbc file parsing)</li>
        <li><strong>Web Server & Async Streaming:</strong> <code>Flask</code>, <code>Flask-SocketIO</code> (WebSockets)</li>
        <li><strong>Frontend:</strong> HTML5, CSS3, Vanilla JS</li>
        <li><strong>Validation:</strong> <code>pytest</code> (Automated decoding assertions)</li>
    </ul>

    <h2>🚀 Getting Started</h2>

    <h3>Prerequisites</h3>
    <p>You need Python 3.8+ installed. All network emulation runs on local memory, so no physical CAN hardware (like a PCAN or Kvaser) is required.</p>

    <h3>Installation</h3>
    <pre><code># 1. Clone the repository
git clone https://github.com/yourusername/can-bus-simulator.git
cd can-bus-simulator

# 2. (Optional but recommended) Set up a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install the required libraries
pip install python-can cantools flask flask-socketio pytest
</code></pre>

    <h3>Running the System</h3>
    <p>To launch the complete suite (Multi-node simulator + Web Server + WebSocket Stream):</p>
    <pre><code>python app.py</code></pre>
    <p>Once the terminal indicates the server is online, open your web browser and navigate to <code>http://127.0.0.1:5000</code> to view the live dashboard.</p>

    <h3>Running the Tests</h3>
    <p>To verify the decoding logic is functioning correctly against the <code>network.dbc</code> file:</p>
    <pre><code>pytest test_decoder.py</code></pre>

    <h2>📁 Project Structure</h2>
    <pre><code>/can-bus-simulator
│
├── app.py                 # Main application (Flask server, WebSockets, ECU Threads)
├── network.dbc            # The database dictionary mapping Hex IDs to physical signals
├── sample_data.log        # Historical drive data for the Ghost Car replay feature
├── test_decoder.py        # Pytest assertions for validation
│
└── /templates
    └── index.html         # The WebSockets frontend dashboard
</code></pre>

    <h2>🤝 Contributing</h2>
    <p>This project was built primarily as a learning exercise in embedded networking and protocol simulation. If you want to expand it (perhaps by adding a UDS diagnostic layer or integrating with hardware via `serial`), feel free to fork the repo and submit a PR!</p>
</body>
</html>
