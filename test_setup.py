#!/usr/bin/env python3
"""
Test Setup for XML-MCP Template Dual Server Architecture

This script validates that both servers can be imported and basic functionality works.
Run this before starting the servers to check for any configuration issues.
"""

import sys
import json
import traceback
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Test standard library imports
        import asyncio
        import logging
        import json
        from datetime import datetime
        from pathlib import Path
        print("✓ Standard library imports OK")
        
        # Test Flask imports
        from flask import Flask, request, jsonify
        from flask_cors import CORS
        print("✓ Flask imports OK")
        
        # Test MCP imports  
        from mcp.server import Server
        from mcp.server.models import InitializationOptions
        from mcp.types import CallToolResult, ListToolsResult, TextContent, Tool
        print("✓ MCP imports OK")
        
        # Test XML processing
        from lxml import etree
        print("✓ lxml import OK")
        
        # Test database
        from tinydb import TinyDB, Query
        print("✓ tinydb import OK")
        
        # Test HTTP client
        import aiohttp
        print("✓ aiohttp import OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_flask_app():
    """Test Flask app creation"""
    print("\n🔍 Testing Flask app creation...")
    
    try:
        # Add app directory to path
        sys.path.insert(0, str(Path(__file__).parent))
        
        from app import create_app
        
        app = create_app()
        print("✓ Flask app created successfully")
        
        # Test app configuration
        assert app.config['JSON_SORT_KEYS'] == False
        print("✓ Flask app configuration OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        traceback.print_exc()
        return False

def test_processors():
    """Test XML processor functionality"""
    print("\n🔍 Testing XML processors...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        
        from app.processors.xml_processor import XMLProcessor
        from app.processors.data_manager import DataManager
        
        # Test XMLProcessor
        processor = XMLProcessor()
        
        sample_content = "# Test\nThis is a test document with **bold** text."
        analysis = processor.analyze_input(sample_content, "markdown")
        
        assert "word_count" in analysis
        assert "complexity_score" in analysis
        assert analysis["input_type"] == "markdown"
        print("✓ XMLProcessor analysis OK")
        
        # Test XML generation
        xml_output = processor.generate_xml_output(analysis, "test-001")
        assert "<Output" in xml_output
        assert "test-001" in xml_output
        print("✓ XMLProcessor XML generation OK")
        
        # Test DataManager
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            data_manager = DataManager(Path(tmp.name))
            
            # Test data storage
            test_data = {"test": "data", "timestamp": "2024-01-01"}
            success = data_manager.store_result("test-id", test_data)
            assert success
            print("✓ DataManager storage OK")
            
            # Test data retrieval
            retrieved = data_manager.get_result("test-id")
            assert retrieved is not None
            assert retrieved["test"] == "data"
            print("✓ DataManager retrieval OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Processor test failed: {e}")
        traceback.print_exc()
        return False

def test_mcp_server():
    """Test MCP server creation"""
    print("\n🔍 Testing MCP server...")
    
    try:
        from mcp.server import Server
        
        server = Server("test-server")
        print("✓ MCP server created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        traceback.print_exc()
        return False

def test_directory_structure():
    """Test that all required directories and files exist"""
    print("\n🔍 Testing directory structure...")
    
    base_dir = Path(__file__).parent
    
    required_files = [
        "server.py",
        "run.py", 
        "requirements.txt",
        "README.md",
        "app/__init__.py",
        "app/routes/__init__.py",
        "app/routes/api.py",
        "app/processors/__init__.py",
        "app/processors/xml_processor.py", 
        "app/processors/data_manager.py",
        "schemas/template-schema.xml",
        "examples/sample-input.md",
        "examples/sample-output.xml"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = base_dir / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print("✓ All required files present")
        return True

def test_xml_schema():
    """Test XML schema validity"""
    print("\n🔍 Testing XML schema...")
    
    try:
        from lxml import etree
        
        schema_path = Path(__file__).parent / "schemas" / "template-schema.xml"
        
        if not schema_path.exists():
            print("❌ Schema file not found")
            return False
        
        # Parse schema
        with open(schema_path, 'r') as f:
            schema_doc = etree.parse(f)
        
        print("✓ Schema file is well-formed XML")
        
        # Validate as XSD
        schema = etree.XMLSchema(schema_doc)
        print("✓ Schema is valid XSD")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("XML-MCP Template Setup Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Directory Structure", test_directory_structure),
        ("XML Schema", test_xml_schema),
        ("Flask App", test_flask_app),
        ("Processors", test_processors),
        ("MCP Server", test_mcp_server)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status:8} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your XML-MCP template is ready for prime time!")
        print("\nNext steps:")
        print("1. Start the integrated system: python server.py")
        print("   (This will automatically launch both MCP + Flask servers)")
        print("2. Test with Claude or MCP client")
        print("3. Or test Flask API directly at http://localhost:5000")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())