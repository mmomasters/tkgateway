#!/usr/bin/env python3
"""
Gateway Benchmark Tool
Measures response times for The Keys gateway endpoints
and provides recommendations for rate limiting
"""

import time
import json
import sys
import urllib.request
import urllib.parse
from statistics import mean, median, stdev
from datetime import datetime

class GatewayBenchmark:
    def __init__(self, host, config_file="config.json"):
        self.host = host
        self.results = []
        self.config_file = config_file
        
    def benchmark_request(self, url, method="GET", data=None, description=""):
        """Benchmark a single request and return timing info"""
        try:
            start_time = time.time()
            
            if method == "GET":
                req = urllib.request.Request(url, method="GET")
            else:  # POST
                req = urllib.request.Request(url, data=data if data else b"", method="POST")
            
            with urllib.request.urlopen(req, timeout=10) as response:
                response_data = response.read().decode('utf-8')
                end_time = time.time()
                
                result = {
                    "url": url,
                    "method": method,
                    "description": description,
                    "status": response.status,
                    "response_time": end_time - start_time,
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.results.append(result)
                return result
                
        except Exception as e:
            end_time = time.time()
            result = {
                "url": url,
                "method": method,
                "description": description,
                "status": None,
                "response_time": end_time - start_time,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results.append(result)
            return result
    
    def run_benchmark_suite(self, iterations=5):
        """Run a comprehensive benchmark suite"""
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║         The Keys Gateway Benchmark Tool                      ║
║         Host: {self.host:45s} ║
║         Iterations: {iterations:2d}                                         ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        base_url = f"http://{self.host}"
        
        # Define test endpoints
        tests = [
            {"url": f"{base_url}/status", "method": "GET", "desc": "Gateway Status"},
            {"url": f"{base_url}/lockers", "method": "GET", "desc": "List Lockers"},
        ]
        
        print("\n🔍 Running benchmark tests...")
        print("=" * 70)
        
        for test in tests:
            print(f"\n📊 Testing: {test['desc']} ({test['method']} {test['url']})")
            times = []
            
            for i in range(iterations):
                result = self.benchmark_request(
                    test['url'], 
                    test['method'],
                    description=test['desc']
                )
                
                if result['success']:
                    times.append(result['response_time'])
                    print(f"  ✅ Request {i+1}/{iterations}: {result['response_time']:.3f}s (HTTP {result['status']})")
                else:
                    print(f"  ❌ Request {i+1}/{iterations}: FAILED - {result.get('error', 'Unknown error')}")
                
                # Small delay between requests to avoid overwhelming the server
                if i < iterations - 1:
                    time.sleep(0.5)
            
            if times:
                print(f"\n  📈 Statistics:")
                print(f"     Mean:   {mean(times):.3f}s")
                print(f"     Median: {median(times):.3f}s")
                print(f"     Min:    {min(times):.3f}s")
                print(f"     Max:    {max(times):.3f}s")
                if len(times) > 1:
                    print(f"     StdDev: {stdev(times):.3f}s")
    
    def generate_report(self):
        """Generate a comprehensive benchmark report"""
        print("\n" + "=" * 70)
        print("📊 BENCHMARK REPORT")
        print("=" * 70)
        
        if not self.results:
            print("❌ No benchmark data available")
            return
        
        successful_results = [r for r in self.results if r['success']]
        failed_results = [r for r in self.results if not r['success']]
        
        print(f"\n📈 Overall Statistics:")
        print(f"   Total Requests:      {len(self.results)}")
        print(f"   Successful:          {len(successful_results)}")
        print(f"   Failed:              {len(failed_results)}")
        
        if successful_results:
            response_times = [r['response_time'] for r in successful_results]
            print(f"\n⏱️  Response Time Statistics:")
            print(f"   Average:    {mean(response_times):.3f}s")
            print(f"   Median:     {median(response_times):.3f}s")
            print(f"   Fastest:    {min(response_times):.3f}s")
            print(f"   Slowest:    {max(response_times):.3f}s")
            if len(response_times) > 1:
                print(f"   Std Dev:    {stdev(response_times):.3f}s")
            
            # Rate limiting recommendations
            avg_time = mean(response_times)
            print(f"\n💡 Rate Limiting Recommendations:")
            print(f"   Based on average response time of {avg_time:.3f}s:")
            
            # Conservative recommendation: wait 2x average response time
            recommended_delay = max(avg_time * 2, 1.0)
            print(f"   • Minimum delay between requests: {recommended_delay:.2f}s")
            print(f"   • Maximum safe request rate: {1/recommended_delay:.2f} requests/second")
            print(f"   • Recommended for bulk operations: {recommended_delay:.2f}s delay")
            
            # For discovery tool with many concurrent requests
            discovery_delay = max(avg_time * 0.5, 0.2)
            print(f"   • For discovery tool (lighter requests): {discovery_delay:.2f}s delay")
            max_workers = min(int(1 / discovery_delay), 5)
            print(f"   • Recommended max workers for discovery: {max_workers}")
        
        # Save detailed results to file
        report_file = f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "host": self.host,
                "timestamp": datetime.now().isoformat(),
                "results": self.results,
                "summary": {
                    "total_requests": len(self.results),
                    "successful": len(successful_results),
                    "failed": len(failed_results),
                    "avg_response_time": mean([r['response_time'] for r in successful_results]) if successful_results else None
                }
            }, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        print("\n✅ Benchmark complete!\n")


def main():
    # Try to load gateway from config.json
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            default_host = config.get("gateway", "192.168.0.129")
    except:
        default_host = "192.168.0.129"
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = default_host
        print(f"No host specified, using from config.json: {host}")
    
    # Remove protocol if present
    host = host.replace("http://", "").replace("https://", "")
    
    iterations = 5
    if len(sys.argv) > 2:
        try:
            iterations = int(sys.argv[2])
        except:
            print(f"Invalid iterations count, using default: {iterations}")
    
    benchmark = GatewayBenchmark(host)
    benchmark.run_benchmark_suite(iterations)
    benchmark.generate_report()


if __name__ == "__main__":
    main()
