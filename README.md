# The Keys Gateway Control Script

This script allows controlling TheKeys smart locks via the gateway.

## Installation

Transfer both `lock.py` and `config.json` to your Raspberry Pi. Run both files in the same directory.

```bash
scp lock.py config.json kolna@raspberrypi:~/
sesh kolna@raspberrypi
chmod +x lock.py
```

## Configuration

Edit `config.json` to add/change gateway IP and locker identifiers/codes.

```json
{
    "gateway": "192.168.0.129",
    "lockers": {
        "1A": {
            "identifier": "3718",
            "code": "dD0ahvPDpKmQxazp"
        }
        ...
    }
}
```

## Usage

### Gateway Commands

```bash
./lock.py list     # List all connected lockers with identifiers, battery, RSSI
./lock.py status   # Get gateway status (version, current action)
./lock.py sync     # Synchronize gateway with server
./lock.py update   # Update gateway firmware
```

### Locker Commands

```bash
./lock.py <locker_name> <action>
```

Available lockers: 1A, 1B, 1C, 1D

Available actions:
- `open`: Unlock the locker
- `close`: Lock the locker
- `calibrate`: Calibrate the lock mechanism
- `status`: Query lock status (open/closed, battery, position)
- `sync`: Synchronize locker with gateway
- `update`: Update locker firmware

### Examples

```bash
./lock.py 1A open
./lock.py 1B close
./lock.py 1C calibrate
./lock.py 1D status
./lock.py 1A sync
./lock.py list
./lock.py update
```

## Getting Share Codes

1. Visit https://api.the-keys.fr
2. Login with your account
3. Create a gateway share link for each locker
4. Copy the generated share code
5. Add to config.json under the appropriate locker

## Codes Reference

- **49**: Door Closed
- **50**: Door Open
- **0**: Success
- Other codes: Check gateway logs or wiki for errors

## Requirements

- Python 3
- Network access to the gateway IP (default 192.168.0.129)

## Troubleshooting

- Ensure gateway IP is correct in config.json
- Share codes must be paired via the TheKeys app/website
- Locker firmware v57+ required for real-time status