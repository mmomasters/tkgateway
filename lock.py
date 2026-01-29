#!/usr/bin/env python3

import hmac
import hashlib
import base64
import time
import sys
import json
import urllib.request
import urllib.parse

class Gateway:
    def __init__(self, host, debug=False):
        self.debug = debug
        self.host = host

    def action(self, action_type, identifier, code):
        ts = str(int(time.time()))
        hm = hmac.new(code.encode("ascii"), ts.encode("ascii"), hashlib.sha256)
        hash = base64.b64encode(hm.digest()).decode('ascii')
        url = f"http://{self.host}/{action_type}"
        data = urllib.parse.urlencode({"hash": hash, "identifier": identifier, "ts": ts}).encode("ascii")
        print(f"URL: {url}")
        print(f"Data: {data.decode()}")
        req = urllib.request.Request(url, data=data)
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res = response.read().decode('utf-8')
                print("Response:", res)
                resp = json.loads(res)
                return resp
        except Exception as e:
            print("Error:", e)
            return None

    def open(self, identifier, code):
        return self.action("open", identifier, code)

    def close(self, identifier, code):
        return self.action("close", identifier, code)

    def calibrate(self, identifier, code):
        return self.action("calibrate", identifier, code)

    def locker_status(self, identifier, code):
        return self.action("locker_status", identifier, code)

    def synchronize_locker(self, identifier):
        # POST to /locker/synchronize with identifier only
        url = f"http://{self.host}/locker/synchronize"
        data = urllib.parse.urlencode({"identifier": identifier}).encode("ascii")
        print(f"URL: {url}")
        print(f"Data: {data.decode()}")
        req = urllib.request.Request(url, data=data)
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res = response.read().decode('utf-8')
                print("Response:", res if res else "(empty)")
                if res:
                    resp = json.loads(res)
                    return resp
                else:
                    print("Success: Command completed (empty response)")
                    return {"status": "ok"}
        except json.JSONDecodeError as e:
            print("JSON Error:", e)
            print("Success: Command completed (invalid JSON)")
            return {"status": "ok"}
        except Exception as e:
            print("Error:", e)
            return None

    def update_locker(self, identifier):
        # POST to /locker/update with identifier only
        url = f"http://{self.host}/locker/update"
        data = urllib.parse.urlencode({"identifier": identifier}).encode("ascii")
        print(f"URL: {url}")
        print(f"Data: {data.decode()}")
        req = urllib.request.Request(url, data=data)
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res = response.read().decode('utf-8')
                print("Response:", res if res else "(empty)")
                if res:
                    resp = json.loads(res)
                    return resp
                else:
                    print("Success: Command completed (empty response)")
                    return {"status": "ok"}
        except json.JSONDecodeError as e:
            print("JSON Error:", e)
            print("Success: Command completed (invalid JSON)")
            return {"status": "ok"}
        except Exception as e:
            print("Error:", e)
            return None

    def synchronize(self):
        # GET /synchronize
        url = f"http://{self.host}/synchronize"
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res = response.read().decode('utf-8')
                print("Response:", res)
                resp = json.loads(res)
                return resp
        except Exception as e:
            print("Error:", e)
            return None

    def update(self):
        # POST /update with no data?
        url = f"http://{self.host}/update"
        req = urllib.request.Request(url, data=b"")
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res = response.read().decode('utf-8')
                print("Response:", res)
                resp = json.loads(res)
                return resp
        except Exception as e:
            print("Error:", e)
            return None

    def status_gateway(self):
        # GET /status
        url = f"http://{self.host}/status"
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res = response.read().decode('utf-8')
                print("Response:", res)
                resp = json.loads(res)
                return resp
        except Exception as e:
            print("Error:", e)
            return None

    def search(self):
        url = f"http://{self.host}/lockers"
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res = response.read().decode('utf-8')
                resp = json.loads(res)
                print("Lockers:", json.dumps(resp, indent=2))
                return resp
        except Exception as e:
            print("Error:", e)
            return None

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

lockers = config["lockers"]
host = config["gateway"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  ./lock.py <gateway_command>")
        print("  ./lock.py <locker_name> <locker_action>")
        print("")
        print("Gateway commands:")
        print("  ./lock.py list       - Search for all lockers (GET /lockers)")
        print("  ./lock.py search     - Search for all lockers (alias for 'list')")
        print("  ./lock.py sync       - Synchronize gateway (GET /synchronize)")
        print("  ./lock.py update     - Update gateway (POST /update)")
        print("  ./lock.py status     - Gateway status (GET /status)")
        print("")
        print("Locker actions:")
        print("  ./lock.py <locker> open       - Open locker (POST /open)")
        print("  ./lock.py <locker> close      - Close locker (POST /close)")
        print("  ./lock.py <locker> calibrate  - Calibrate locker (POST /calibrate)")
        print("  ./lock.py <locker> status     - Get locker status (POST /locker_status)")
        print("  ./lock.py <locker> sync       - Synchronize locker (POST /locker/synchronize)")
        print("  ./lock.py <locker> update     - Update locker (POST /locker/update)")
        sys.exit(1)

    gw = Gateway(host)

    arg1 = sys.argv[1]

    if arg1 == "list" or arg1 == "search":
        gw.search()
    elif arg1 in ["sync", "update", "status"]:
        # Gateway wide
        if arg1 == "sync":
            gw.synchronize()
        elif arg1 == "update":
            gw.update()
        elif arg1 == "status":
            gw.status_gateway()
    else:
        if len(sys.argv) < 3:
            print("Need action for locker.")
            sys.exit(1)
        locker_name = arg1
        action = sys.argv[2]

        if locker_name not in lockers:
            print("Unknown locker:", locker_name)
            sys.exit(1)

        locker = lockers[locker_name]
        identifier = locker["identifier"]

        if action in ["open", "close", "calibrate", "status"]:
            code = locker["code"]
            if action == "open":
                gw.open(identifier, code)
            elif action == "close":
                gw.close(identifier, code)
            elif action == "calibrate":
                gw.calibrate(identifier, code)
            elif action == "status":
                gw.locker_status(identifier, code)
        elif action in ["sync", "update"]:
            if action == "sync":
                gw.synchronize_locker(identifier)
            elif action == "update":
                gw.update_locker(identifier)
        else:
            print("Unknown action:", action)
