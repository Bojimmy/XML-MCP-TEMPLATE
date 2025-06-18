#!/usr/bin/env python3
"""
Test XML-MCP Template with Mock Data

This script demonstrates the XML-MCP template functionality using sample data.
It shows how the tools work with realistic content and generates example outputs.
"""

import asyncio
import json
import requests
import time
from pathlib import Path

def load_sample_content():
    """Load sample PRD content for testing"""
    base_dir = Path(__file__).parent
    prd_file = base_dir / "examples" / "sample-prd.md"
    
    if prd_file.exists():
        with open(prd_file, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return """# Sample Project Requirements
        
## Overview
This is a sample project requirements document for testing the XML-MCP template.

## Features
- Feature 1: Core functionality
- Feature 2: Advanced features  
- Feature 3: Integration capabilities

## Technical Requirements
- Web-based application
- Mobile responsive design
- API-first architecture
- Cloud deployment

## Success Metrics
- User adoption: 1000+ active users
- Performance: Sub-2s page loads
- Reliability: 99.9% uptime
"""

async def test_flask_api():
    """Test the Flask API endpoints with mock data"""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing XML-MCP Template with Mock Data")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed: {health_data.get('status')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Analyze Sample PRD
    print("\n2. Testing analysis with sample PRD...")
    sample_content = load_sample_content()
    
    analyze_data = {
        "content": sample_content,
        "input_type": "markdown",
        "options": {
            "extract_features": True,
            "complexity_analysis": True
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/analyze",
            json=analyze_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                analysis = result.get("analysis", {})
                print("✅ Analysis completed successfully")
                print(f"   📊 Word count: {analysis.get('word_count', 'N/A')}")
                print(f"   📝 Input type: {analysis.get('input_type', 'N/A')}")
                print(f"   🔢 Complexity score: {analysis.get('complexity_score', 'N/A')}")
                print(f"   📋 Features found: {len(analysis.get('features', []))}")
                
                # Store analysis for next test
                analysis_result = analysis
            else:
                print(f"❌ Analysis failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Analysis request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False
    
    # Test 3: Generate XML Task Packet
    print("\n3. Testing XML generation with task packet template...")
    
    xml_data = {
        "analysis": analysis_result,
        "output_id": "test-task-packet-001",
        "template": "task_packet",
        "options": {
            "include_timeline": True,
            "include_risks": True
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json=xml_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                xml_output = result.get("xml_output", "")
                print("✅ XML generation completed")
                print(f"   📄 XML length: {len(xml_output)} characters")
                print(f"   📦 Template: task_packet")
                
                # Save sample output
                output_file = Path(__file__).parent / "examples" / "generated-task-packet.xml"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(xml_output)
                print(f"   💾 Saved to: {output_file}")
            else:
                print(f"❌ XML generation failed: {result.get('error')}")
                return False
        else:
            print(f"❌ XML generation request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ XML generation error: {e}")
        return False
    
    # Test 4: Complete Workflow (Process)
    print("\n4. Testing complete workflow...")
    
    process_data = {
        "content": "# Quick Test Document\n\nThis is a quick test of the complete workflow.\n\n## Requirements\n- Feature A\n- Feature B\n- Feature C",
        "input_type": "markdown",
        "output_id": "test-workflow-001", 
        "template": "analysis_report",
        "options": {
            "detailed_analysis": True
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/process",
            json=process_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Complete workflow succeeded")
                print(f"   🆔 Processing ID: {result.get('processing_id')}")
                print(f"   📊 Analysis completed: {result.get('analysis_completed', False)}")
                print(f"   📄 XML generated: {result.get('xml_generated', False)}")
            else:
                print(f"❌ Workflow failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Workflow request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Workflow error: {e}")
        return False
    
    # Test 5: List Templates
    print("\n5. Testing templates endpoint...")
    
    try:
        response = requests.get(f"{base_url}/api/templates", timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                templates = result.get("templates", [])
                print(f"✅ Templates listed: {len(templates)} available")
                for template in templates:
                    print(f"   📋 {template.get('name')}: {template.get('description')}")
            else:
                print(f"❌ Templates listing failed: {result.get('error')}")
        else:
            print(f"❌ Templates request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Templates error: {e}")
    
    # Test 6: List Data
    print("\n6. Testing data listing...")
    
    try:
        response = requests.get(f"{base_url}/api/data", timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                data_entries = result.get("data", [])
                print(f"✅ Data entries: {len(data_entries)} found")
                for entry in data_entries[:3]:  # Show first 3
                    print(f"   📝 {entry.get('id')}: {entry.get('type', 'Unknown')} ({entry.get('created', 'No date')})")
            else:
                print(f"❌ Data listing failed: {result.get('error')}")
        else:
            print(f"❌ Data request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Data listing error: {e}")
    
    print("\n🎉 Mock data testing completed!")
    print("\n📁 Generated files:")
    print("   - examples/generated-task-packet.xml")
    print("   - storage/data.json (TinyDB storage)")
    
    return True

async def demonstrate_mcp_tools():
    """Demonstrate what the MCP tools would do (simulated)"""
    print("\n" + "=" * 50)
    print("🔧 MCP Tools Demonstration (Simulated)")
    print("=" * 50)
    
    sample_content = load_sample_content()
    
    print("\n🛠️  Available MCP Tools:")
    tools = [
        ("analyze_input", "Analyze content and extract information"),
        ("generate_xml", "Generate XML from analysis results"),
        ("process_input", "Complete workflow (analyze + generate XML)"),
        ("get_status", "Check processing status by ID"),
        ("list_data", "List all saved data entries"),
        ("get_data", "Retrieve specific data by ID"),
        ("delete_data", "Delete data by ID"),
        ("list_templates", "List available XML templates"),
        ("health_check", "Check Flask server health")
    ]
    
    for tool_name, description in tools:
        print(f"   🔧 {tool_name}: {description}")
    
    print(f"\n📝 Sample content loaded: {len(sample_content)} characters")
    print("   Content preview:", sample_content[:100].replace('\n', ' ') + "...")
    
    print("\n✨ When used with Claude, these tools would:")
    print("   1. 📊 Analyze the PRD content for structure and completeness")
    print("   2. 🏗️  Extract requirements, features, and stakeholders")
    print("   3. 📄 Generate structured XML task packets for project management")
    print("   4. 🔍 Provide analysis reports with recommendations")
    print("   5. 💾 Store all results for later retrieval and modification")
    
    return True

def main():
    """Main test function"""
    print("🚀 XML-MCP Template Mock Data Testing")
    print("This script tests the template with realistic sample data")
    print("Make sure the server is running: python server.py")
    print()
    
    # Wait a moment for user to read
    time.sleep(2)
    
    try:
        # Test Flask API
        success = asyncio.run(test_flask_api())
        
        if success:
            # Demonstrate MCP tools
            asyncio.run(demonstrate_mcp_tools())
            
            print("\n" + "=" * 50)
            print("✅ All tests completed successfully!")
            print("\n🎯 Next Steps:")
            print("   1. ✅ The template is working correctly with mock data")
            print("   2. 🔧 Customize the processors for your specific use case")
            print("   3. 📋 Add your own XML templates in schemas/")
            print("   4. 🎨 Modify the analysis logic in app/processors/")
            print("   5. 🔗 Add the server to your Claude Desktop configuration")
            
            print("\n🔗 Claude Desktop Integration:")
            print('   Add this to your Claude Desktop MCP configuration:')
            print('   {')
            print('     "xml-mcp-template": {')
            print('       "command": "/usr/bin/python3",')
            print('       "args": ["/Users/bobdallavia/XML-MCP-TEMPLATE/server.py"]')
            print('     }')
            print('   }')
        else:
            print("\n❌ Some tests failed. Check that the server is running.")
            
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")

if __name__ == "__main__":
    main()