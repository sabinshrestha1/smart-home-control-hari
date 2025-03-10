from flask import Flask, render_template, request, jsonify
import serial
import time
import os

app = Flask(__name__)

SERIAL_PORT = "COM6"
BAUD_RATE = 115200
ser = None

def initialize_serial():
    global ser
    try:
        if ser and ser.is_open:
            ser.close()
            
        print(f"Attempting to connect to {SERIAL_PORT}...")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        print(f"Connected to {SERIAL_PORT} successfully!")
        return True
    except Exception as e:
        print(f"Connection failed: {str(e)}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control', methods=['POST'])
def control():
    if not ser or not ser.is_open:
        return jsonify({'error': 'Serial port not connected'})
    
    try:
        command = request.form['command']
        print(f"Received command: {command}")
        
        # Clear buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # Send command
        ser.write(f"{command}\n".encode('utf-8'))
        time.sleep(0.5)  # Increased delay for ESP response
        
        # Read response
        response = ser.readline().decode('utf-8').strip()
        print(f"ESP response: {response}")
        return jsonify({'response': response})
        
    except Exception as e:
        print(f"Error handling command: {str(e)}")
        return jsonify({'error': str(e)})

def run_server():
    global ser
    try:
        if initialize_serial():
            app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        else:
            print("Failed to initialize serial connection")
    except KeyboardInterrupt:
        pass
    finally:
        if ser and ser.is_open:
            ser.close()
            print("Serial connection closed")

if __name__ == '__main__':
    run_server()