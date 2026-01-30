# Rate Limiting & Benchmarking Updates

## Summary

This update adds comprehensive rate limiting and benchmarking capabilities to prevent overloading the remote gateway server while measuring its performance characteristics.

## Changes Made

### 1. New Tool: benchmark.py ✨

A comprehensive benchmarking tool that:
- Measures response times for gateway endpoints (/status, /lockers)
- Calculates statistics (mean, median, min, max, standard deviation)
- Provides personalized rate limiting recommendations
- Saves detailed reports to JSON files for analysis

**Usage:**
```bash
./benchmark.py                    # Uses gateway from config.json
./benchmark.py 192.168.0.129      # Specify gateway address
./benchmark.py gateway.local 10   # Specify address and iterations (default: 5)
```

**Output includes:**
- Response time for each request
- Statistical analysis
- Rate limiting recommendations based on actual server performance
- Saved report: `benchmark_report_YYYYMMDD_HHMMSS.json`

### 2. Enhanced: lock.py 🔒

**Added Rate Limiting:**
- New `_rate_limit()` method enforces minimum delay between requests
- Applied to ALL operations: open, close, calibrate, status, sync, update
- Configurable via `rate_limit_delay` in config.json (default: 1.0 second)
- Prevents overwhelming the gateway server

**How it works:**
- Tracks timestamp of last request
- Automatically sleeps if requests come too quickly
- Silent operation (no delay messages unless debug mode)
- Zero impact on functionality, only adds safety delays

**Configuration:**
Add to your config.json:
```json
{
    "gateway": "192.168.0.129",
    "rate_limit_delay": 1.0,
    "lockers": { ... }
}
```

### 3. Enhanced: discover.py 🔍

**Rate Limiting Improvements:**
- Reduced max concurrent workers from 10 to 3 (safer for server)
- Added 0.3s delay between endpoint tests
- Added 0.1s delay between port scans
- Configurable delay via command line argument

**Usage:**
```bash
./discover.py gateway.local        # Default 0.3s delay
./discover.py gateway.local 0.5    # Custom 0.5s delay
```

**Benefits:**
- Prevents port scan flooding
- Gentler on the server
- Still fast enough for practical use
- Shows rate limit configuration in output

### 4. Updated: config.example.json 📝

Added `rate_limit_delay` parameter with default value of 1.0 second.

### 5. Updated: README.md 📚

Comprehensive documentation updates:
- Benchmarking tool documentation
- Rate limiting configuration guide
- Troubleshooting section for rate limiting issues
- Examples and recommended values
- Performance testing guidelines

## Rate Limiting Guidelines

### Recommended Delays:

| Environment | Recommended Delay | Notes |
|-------------|------------------|-------|
| Local Network | 0.5 - 1.0s | Fast, reliable connection |
| Remote Server | 1.0 - 2.0s | Internet latency considered |
| Slow/Busy Server | 2.0+ seconds | Prevent overload |

### Best Practices:

1. **Run benchmark first:** `./benchmark.py` to get personalized recommendations
2. **Start conservative:** Use 1.0s delay initially
3. **Adjust based on results:** Increase if you see timeouts/errors
4. **Monitor gateway:** Check gateway logs for rate limiting errors

## Technical Details

### Rate Limiting Implementation

**lock.py:**
```python
def _rate_limit(self):
    """Enforce rate limiting between requests"""
    current_time = time.time()
    time_since_last_request = current_time - self.last_request_time
    
    if time_since_last_request < self.rate_limit_delay:
        sleep_time = self.rate_limit_delay - time_since_last_request
        time.sleep(sleep_time)
    
    self.last_request_time = time.time()
```

This method is called before every HTTP request, ensuring minimum delay.

**discover.py:**
- Uses `time.sleep(delay)` before each endpoint test
- ThreadPoolExecutor limited to MAX_WORKERS = 3
- Sequential delays prevent burst requests

### Backward Compatibility

- All changes are backward compatible
- If `rate_limit_delay` is not in config.json, defaults to 1.0 second
- Existing scripts continue to work with new protection
- No breaking changes to API or command line interface

## Testing Recommendations

1. **Benchmark your setup:**
   ```bash
   ./benchmark.py
   ```

2. **Review recommendations:**
   Check the output for personalized delay settings

3. **Update config.json:**
   Set `rate_limit_delay` based on benchmark results

4. **Test operations:**
   ```bash
   ./lock.py status
   ./lock.py list
   ./lock.py 1A status
   ```

5. **Monitor for issues:**
   - Watch for timeout errors
   - Check gateway server logs
   - Adjust delay if needed

## Migration Guide

If you have an existing config.json:

1. Add the new parameter:
   ```json
   "rate_limit_delay": 1.0,
   ```

2. Position doesn't matter, but typically after "gateway"

3. Run benchmark to optimize:
   ```bash
   ./benchmark.py
   ```

4. Update delay based on recommendations

## Files Modified

- ✅ `lock.py` - Added rate limiting to all requests
- ✅ `discover.py` - Reduced concurrency, added delays
- ✅ `config.example.json` - Added rate_limit_delay parameter
- ✅ `README.md` - Comprehensive documentation updates
- ✨ `benchmark.py` - New benchmarking tool (created)
- 📝 `CHANGES.md` - This file (created)

## Benefits

✅ **Server Protection:** Prevents accidental server overload  
✅ **Performance Insights:** Benchmark tool shows actual performance  
✅ **Configurable:** Easy to adjust based on your needs  
✅ **Transparent:** Works silently without user intervention  
✅ **Safe Defaults:** Conservative 1.0s delay out of the box  
✅ **Personalized:** Recommendations based on your server  

## Questions?

- Check README.md for usage examples
- Run `./benchmark.py` to analyze your gateway
- Adjust `rate_limit_delay` in config.json as needed
- Monitor server logs for rate limiting issues
