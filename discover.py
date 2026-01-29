#!/usr/bin/env python3
"""
Gateway Discovery Tool
Scans for available ports and API endpoints on The Keys gateway
"""

import socket
import urllib.request
import urllib.parse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Common ports to check
COMMON_PORTS = [
    80, 443, 8080, 8443, 8888, 9090, 9856,  # HTTP/HTTPS variants
    3000, 5000, 8000, 8001, 8888, 9000, 9001,  # Development servers
]

# Known and potential API endpoints
API_ENDPOINTS = {
    # Known working endpoints
    "GET": [
        "/status",
        "/synchronize", 
        "/lockers",
        "/version",
        "/info",
        "/health",
        "/api",
        "/api/status",
        "/api/lockers",
        "/locks",
        "/devices",
        "/",
    ],
    "POST": [
        "/open",
        "/close",
        "/calibrate",
        "/locker_status",
        "/locker/synchronize",
        "/locker/update",
        "/update",
        "/lock",
        "/unlock",
        "/sync",
        "/api/open",
        "/api/close",
        "/api/lock",
        "/api/unlock",
    ]
}


def check_port(host, port, timeout=2):
    """Check if a port is open on the host"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def try_endpoint(url, method="GET", timeout=3):
    """Try to access an endpoint and return the response"""
    try:
        if method == "GET":
            req = urllib.request.Request(url, method="GET")
        else:  # POST
            # Try with empty data
            req = urllib.request.Request(url, data=b"", method="POST")
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status = response.status
            data = response.read().decode('utf-8')
            
            # Try to parse as JSON
            try:
                parsed = json.loads(data)
                return {
                    "status": status,
                    "data": parsed,
                    "raw": data[:200],  # First 200 chars
                    "type": "json"
                }
            except:
                return {
                    "status": status,
                    "data": None,
                    "raw": data[:200],
                    "type": "text"
                }
    except urllib.error.HTTPError as e:
        return {
            "status": e.code,
            "error": str(e),
            "type": "http_error"
        }
    except Exception as e:
        return {
            "error": str(e),
            "type": "exception"
        }


def scan_ports(host):
    """Scan common ports on the host"""
    print(f"\n🔍 Scanning ports on {host}...")
    print("=" * 60)
    
    open_ports = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_port, host, port): port for port in COMMON_PORTS}
        
        for future in as_completed(futures):
            port = futures[future]
            try:
                is_open = future.result()
                if is_open:
                    print(f"✅ Port {port} is OPEN")
                    open_ports.append(port)
            except Exception as e:
                print(f"❌ Error checking port {port}: {e}")
    
    if not open_ports:
        print("❌ No open ports found")
    
    return open_ports


def scan_endpoints(host, port):
    """Scan API endpoints on a specific port"""
    print(f"\n🔍 Scanning API endpoints on {host}:{port}...")
    print("=" * 60)
    
    base_url = f"http://{host}:{port}"
    discovered = {"GET": {}, "POST": {}}
    
    # Try GET endpoints
    print("\n📥 Testing GET endpoints...")
    for endpoint in API_ENDPOINTS["GET"]:
        url = base_url + endpoint
        result = try_endpoint(url, "GET")
        
        if result.get("status") in [200, 201]:
            print(f"✅ {endpoint}")
            if result.get("type") == "json":
                print(f"   Response: {json.dumps(result['data'], indent=2)}")
            else:
                print(f"   Response: {result['raw']}")
            discovered["GET"][endpoint] = result
        elif result.get("status"):
            print(f"⚠️  {endpoint} - HTTP {result['status']}")
        # Don't print errors for each failed endpoint (too noisy)
    
    # Try POST endpoints
    print("\n📤 Testing POST endpoints...")
    for endpoint in API_ENDPOINTS["POST"]:
        url = base_url + endpoint
        result = try_endpoint(url, "POST")
        
        if result.get("status") in [200, 201]:
            print(f"✅ {endpoint}")
            if result.get("type") == "json":
                print(f"   Response: {json.dumps(result['data'], indent=2)}")
            else:
                print(f"   Response: {result['raw']}")
            discovered["POST"][endpoint] = result
        elif result.get("status") in [400]:  # Bad request often means endpoint exists
            print(f"⚠️  {endpoint} - HTTP {result['status']} (endpoint exists, needs parameters)")
            discovered["POST"][endpoint] = result
    
    return discovered


def main():
    if len(sys.argv) < 2:
        print("Usage: ./discover.py <hostname>")
        print("Example: ./discover.py tkgateway.mooo.com")
        sys.exit(1)
    
    host = sys.argv[1].replace("http://", "").replace("https://", "").split(":")[0]
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║         The Keys Gateway Discovery Tool                      ║
║         Scanning: {host:40s} ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Scan for open ports
    open_ports = scan_ports(host)
    
    # Scan endpoints on each open port
    all_discoveries = {}
    for port in open_ports:
        discoveries = scan_endpoints(host, port)
        if discoveries["GET"] or discoveries["POST"]:
            all_discoveries[port] = discoveries
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DISCOVERY SUMMARY")
    print("=" * 60)
    
    if all_discoveries:
        for port, discoveries in all_discoveries.items():
            print(f"\n🔌 Port {port}:")
            if discoveries["GET"]:
                print(f"  GET endpoints: {len(discoveries['GET'])}")
                for endpoint in discoveries["GET"].keys():
                    print(f"    • {endpoint}")
            if discoveries["POST"]:
                print(f"  POST endpoints: {len(discoveries['POST'])}")
                for endpoint in discoveries["POST"].keys():
                    print(f"    • {endpoint}")
    else:
        print("❌ No accessible endpoints discovered")
    
    print("\n✅ Scan complete!\n")


if __name__ == "__main__":
    main()
