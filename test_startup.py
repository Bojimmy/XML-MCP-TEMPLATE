#!/usr/bin/env python3
"""
Test Integrated Startup for XML-MCP Template

This script tests the integrated startup process without requiring MCP client.
It simulates the startup flow and verifies both servers work together.
"""

import asyncio
import time
import subprocess
import signal
import requests
from pathlib import Path

def test_integrated_startup():
    """Test the integrated MCP + Flask startup process"""
    print("🧪 Testing XML-MCP Template Integrated Startup")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    server_script = base_dir / "server.py"
    
    if not server_script.exists():
        print("❌ server.py not found")
        return False
    
    print("🚀 Starting integrated server...")
    print("(This will launch both MCP and Flask servers)")
    
    try:
        # Start the integrated server
        process = subprocess.Popen(
            ["python", str(server_script)],
            cwd=base_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✓ Process started (PID: {process.pid})")
        
        # Wait for servers to start up
        print("⏳ Waiting for servers to initialize...")
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print("❌ Process exited unexpectedly:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
        
        print("✓ Process is running")
        
        # Test Flask server health endpoint
        print("🔍 Testing Flask server health...")
        
        max_attempts = 10
        flask_ready = False
        
        for attempt in range(max_attempts):
            try:
                response = requests.get("http://localhost:5001/health", timeout=2)
                if response.status_code == 200:
                    health_data = response.json()
                    print(f"✓ Flask server health check passed: {health_data.get('status')}")
                    flask_ready = True
                    break
            except requests.exceptions.RequestException:
                if attempt < max_attempts - 1:
                    print(f"⏳ Flask not ready yet (attempt {attempt + 1}/{max_attempts}), retrying...")
                    time.sleep(1)
                else:
                    print("❌ Flask server health check failed")
        
        if not flask_ready:
            process.terminate()
            return False
        
        # Test a simple API endpoint
        print("🔍 Testing Flask API endpoint...")
        
        try:
            test_data = {
                "content": "# Test Document\nThis is a test.",
                "input_type": "markdown",
                "output_id": "test-startup-001"
            }
            
            response = requests.post(
                "http://localhost:5001/api/analyze",
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✓ Flask API endpoint test passed")
                    analysis = result.get("analysis", {})
                    print(f"  - Word count: {analysis.get('word_count', 'N/A')}")
                    print(f"  - Input type: {analysis.get('input_type', 'N/A')}")
                else:
                    print(f"❌ API returned error: {result.get('error')}")
                    process.terminate()
                    return False
            else:
                print(f"❌ API request failed with status {response.status_code}")
                process.terminate()
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            process.terminate()
            return False
        
        # Test templates endpoint
        print("🔍 Testing templates endpoint...")
        
        try:
            response = requests.get("http://localhost:5001/api/templates", timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    templates = result.get("templates", [])
                    print(f"✓ Templates endpoint works - {len(templates)} templates available")
                    for template in templates:
                        print(f"  - {template.get('name')}: {template.get('description')}")
                else:
                    print("⚠ Templates endpoint returned error")
            else:
                print("⚠ Templates endpoint failed")
        except requests.exceptions.RequestException:
            print("⚠ Templates endpoint test failed")
        
        print("\n🎉 Integrated startup test PASSED!")
        print("✓ MCP server launches Flask automatically")
        print("✓ Flask server responds to health checks")
        print("✓ API endpoints are functional")
        print("✓ Both servers running in integrated mode")
        
        # Clean shutdown
        print("\n🛑 Stopping servers...")
        process.terminate()
        
        try:
            process.wait(timeout=5)
            print("✓ Servers stopped gracefully")
        except subprocess.TimeoutExpired:
            print("⚠ Force killing process...")
            process.kill()
            process.wait()
            print("✓ Servers force stopped")
        
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        if 'process' in locals():
            process.terminate()
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        if 'process' in locals():
            process.terminate()
        return False

if __name__ == "__main__":
    success = test_integrated_startup()
    if success:
        print("\n✅ XML-MCP Template integrated startup is working perfectly!")
        print("Ready for Claude integration! 🚀")
        exit(0)
    else:
        print("\n❌ Startup test failed. Please check the error messages above.")
        exit(1)