# pip install pyserial 
import socket
import serial
import serial.tools.list_ports
import struct
import threading
import time

# Configuration
UDP_TO_SERIAL_PORT = 7046  # UDP port for receiving data to send to the serial port
SERIAL_TO_UDP_PORT = [7045,7555]  # UDP port for sending data received from the serial port
UDP_TARGET_IP = "127.0.0.1"  # Target IP for UDP communication
SERIAL_BAUDRATE = 9600
DEVICE_ID = "98D331F71DA0"
DEVICE_ID = "USB-SERIAL CH340"
DEVICE_ID = "E8EB1B9E096A"

# Functions for serial communication
def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"Device: {port.device}")
        print(f"Name: {port.name}")
        print(f"Description: {port.description}")
        print(f"HWID: {port.hwid}")
        print(f"VID: {port.vid}")
        print(f"PID: {port.pid}")
        print(f"Serial Number: {port.serial_number}")
        print(f"Location: {port.location}")
        print(f"Manufacturer: {port.manufacturer}")
        print(f"Product: {port.product}")
        print(f"Interface: {port.interface}")
        print("-" * 40)

def find_device_com(device_id):
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if port.serial_number == device_id:
            return port.device
        if device_id in port.hwid:
            return port.device
        if device_id in port.description:
            return port.device
    return None

# Thread for UDP -> Serial
def udp_to_serial(udp_port, serial_port):
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(("0.0.0.0", udp_port))
    print(f"Listening for UDP data on port {udp_port}...")
    
    while True:
        data, addr = udp_sock.recvfrom(1024)
        print(f"Received from UDP {addr}: {data}")
        serial_port.write(data)

# Thread for Serial -> UDP
def serial_to_udp(serial_port, udp_ip, udp_port):
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Sending serial data to {udp_ip}:{udp_port}...")
    
    while True:
        if serial_port.in_waiting > 0:
            data = serial_port.read(serial_port.in_waiting)
            print(f"Received from Serial: {data}")
            for port in udp_port:
                udp_sock.sendto(data, (udp_ip, port))
        time.sleep(0.01)

# Main
if __name__ == "__main__":
    # List serial ports
    list_serial_ports()
    
    # Find serial device
    com_port = find_device_com(DEVICE_ID)
    if not com_port:
        print(f"Device with ID {DEVICE_ID} not found!")
        exit(1)
    
    print(f"Connecting to {com_port}...")
    serial_port = serial.Serial(com_port, SERIAL_BAUDRATE, timeout=1)
    # Start threads
    udp_thread = threading.Thread(target=udp_to_serial, args=(UDP_TO_SERIAL_PORT, serial_port), daemon=True)
    serial_thread = threading.Thread(target=serial_to_udp, args=(serial_port, UDP_TARGET_IP, SERIAL_TO_UDP_PORT), daemon=True)
    
    udp_thread.start()
    serial_thread.start()    
    # Keep the main thread alive
    try:
        
        print("Press 'E' to exit...")
        while True:
            time.sleep(1)
            if input().strip().upper() == 'E':
                print("Exiting...")
                break
    except KeyboardInterrupt:
        print("Shutting down...")
        serial_port.close()
