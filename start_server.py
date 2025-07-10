#!/usr/bin/env python3
"""
Simple server starter with network diagnostics
"""

import os
import sys
import socket

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address (doesn't actually connect)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "localhost"

def check_port(port):
    """Check if port is available"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', port))
        s.close()
        return True
    except OSError:
        return False

def main():
    print("WMS Application - Server Starter")
    print("=" * 40)
    
    # Check port availability
    port = 5000
    if not check_port(port):
        print(f"⚠ Port {port} is in use. Trying port 5001...")
        port = 5001
        if not check_port(port):
            print(f"⚠ Port {port} is also in use. Please close other applications.")
            sys.exit(1)
    
    # Get network information
    local_ip = get_local_ip()
    
    print(f"✓ Port {port} is available")
    print(f"✓ Local IP detected: {local_ip}")
    
    # Set up environment
    if not os.environ.get("SESSION_SECRET"):
        os.environ["SESSION_SECRET"] = "dev-secret-key-local-2024"
    
    try:
        from app import app
        
        print("\n" + "=" * 40)
        print("Server starting...")
        print("=" * 40)
        print(f"Local access:   http://localhost:{port}")
        print(f"Network access: http://{local_ip}:{port}")
        print("=" * 40)
        print("Login credentials:")
        print("Username: admin")
        print("Password: admin123")
        print("=" * 40)
        print("Press Ctrl+C to stop the server")
        print()
        
        # Start the server
        app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
        
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\n✗ Failed to start server: {e}")
        print("\nTroubleshooting:")
        print("1. Check if another application is using the port")
        print("2. Try running: python install_local_deps.py")
        print("3. Check firewall settings if accessing from network")

if __name__ == "__main__":
    main()