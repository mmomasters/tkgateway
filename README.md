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
    "rate_limit_delay": 1.0,
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

### Rate Limiting Configuration

The `rate_limit_delay` parameter controls the minimum delay (in seconds) between heavy operations (open/close/calibrate/status) to prevent overloading the gateway server.

The `rate_limit_delay_light` parameter controls the delay between light operations (gateway status/list queries).

- **Recommended values (based on benchmark results):**
  - **Heavy operations** (`rate_limit_delay`): `5.0` seconds
    - Locker operations take ~3.6s average to complete
    - Recommended minimum: 5.0s prevents server overload
  - **Light operations** (`rate_limit_delay_light`): `1.0` seconds
    - Gateway queries take ~0.13s average
    - Conservative 1.0s setting provides extra safety margin

**Always run `./benchmark.py` to test your gateway and get personalized recommendations.**

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

## Benchmarking and Performance Testing

### Benchmark Tool

Before using the gateway extensively, it's recommended to benchmark your server's response times:

```bash
./benchmark.py                    # Uses gateway from config.json
./benchmark.py 192.168.0.129      # Specify gateway address
./benchmark.py gateway.local 10   # Specify address and iterations
```

The benchmark tool will:
- Measure response times for common gateway endpoints (status, list)
- **NEW**: Test individual locker status commands (`./lock.py LOCKER_ID status`)
- Automatically detect configured lockers from config.json
- Generate separate statistics for gateway and locker endpoints
- Provide personalized rate limiting recommendations
- Save detailed results to a JSON report file

**Features:**
- Tests gateway endpoints: `/status`, `/lockers`
- Tests locker status for each configured locker with proper HMAC authentication
- Skips lockers with placeholder credentials automatically
- Breaks down performance by endpoint type
- 0.5s delay between requests to prevent server overload

**Example output:**
```
🔐 Testing Locker Status Commands
(Simulating: ./lock.py LOCKER_ID status)

📊 Testing: Locker 1A Status (POST /locker_status)
  ✅ Request 1/5: 0.145s (HTTP 200)
  ...

⏱️  Response Time Statistics (All Endpoints):
   Average:    0.132s
   Median:     0.128s

⏱️  Gateway Endpoints (status, list):
   Average:    0.130s

⏱️  Locker Status Endpoints (./lock.py LOCKER_ID status):
   Average:    0.140s

💡 Rate Limiting Recommendations:
   • Minimum delay between requests: 1.00s
   • For light operations (status/list): 0.20s delay
```

### Gateway Discovery Tool

Scan for available ports and endpoints with built-in rate limiting:

```bash
./discover.py <hostname>           # Uses default 0.3s delay
./discover.py gateway.local 0.5    # Custom 0.5s delay between requests
```

Features:
- Scans common ports (80, 443, 8080, 9856, etc.)
- Tests known API endpoints
- Rate-limited to prevent server overload (configurable)
- Reduced concurrent workers (max 3) for safer scanning

## Requirements

- Python 3 (with standard library)
- Network access to the gateway address (configured in config.json)

## Troubleshooting

- Ensure gateway address is correct in config.json
- Share codes must be paired via the TheKeys app/website
- Locker firmware v57+ required for real-time status
- If requests are timing out or failing:
  - Run `./benchmark.py` to check server response times
  - Increase `rate_limit_delay` in config.json
  - Check network connectivity to the gateway
- If receiving errors about "too many requests":
  - Increase `rate_limit_delay` to 2.0 or higher
  - Reduce concurrent operations

## Rate Limiting Protection

All scripts now include built-in rate limiting to prevent overloading the gateway server:

### lock.py
- Enforces minimum delay between requests (configured via `rate_limit_delay` in config.json)
- Automatically throttles all operations (open, close, status, sync, etc.)
- Silent operation unless debug mode is enabled

### discover.py
- Limited to 3 concurrent workers (reduced from 10)
- 0.3s default delay between endpoint tests
- 0.1s delay between port scans
- Configurable via command line: `./discover.py hostname 0.5`

### benchmark.py
- Built-in 0.5s delay between benchmark iterations
- Provides personalized rate limiting recommendations
- Saves detailed performance reports for analysis
