# The Keys Gateway Control Script

This script allows controlling TheKeys smart locks via the gateway.

## Installation

1. Clone or download this repository
2. Copy `config.example.json` to `config.json`:
   ```bash
   cp config.example.json config.json
   ```
3. Edit `config.json` with your gateway address and locker credentials (see Configuration below)
4. Transfer both `lock.py` and `config.json` to your Raspberry Pi:
   ```bash
   scp lock.py config.json kolna@raspberrypi:~/
   ssh kolna@raspberrypi
   chmod +x lock.py
   ```

**Note:** `config.json` is gitignored to keep your credentials safe. Only `config.example.json` is tracked in the repository.

## Configuration

Edit `config.json` (not the example file) to add your gateway address and locker identifiers/codes.

The gateway address can be either a local IP address (e.g., `192.168.0.129`) or a domain name with port (e.g., `gateway.example.com:9856`).

See `config.example.json` for the template structure:

```json
{
    "gateway": "192.168.0.129",
    "lockers": {
        "1A": {
            "identifier": "YOUR_IDENTIFIER",
            "code": "YOUR_SHARE_CODE"
        },
        "1B": {
            "identifier": "YOUR_IDENTIFIER",
            "code": "YOUR_SHARE_CODE"
        }
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
- Network access to the gateway address (configured in config.json)

## Troubleshooting

- Ensure gateway address is correct in config.json
- Share codes must be paired via the TheKeys app/website
- Locker firmware v57+ required for real-time status
