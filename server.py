#!/usr/bin/env python3
"""
XML-MCP Template Server with Dual Architecture

This MCP server connects to a Flask backend for XML processing.
The dual-server architecture allows for:
- MCP protocol integration with Claude
- REST API endpoints for web UI integration
- Scalable processing architecture

ARCHITECTURE:
1. MCP Server (this file) - Handles Claude integration
2. Flask Server (run.py) - Handles XML processing and storage

USAGE:
1. Start MCP server: python server.py
   (Flask server will be launched automatically)
"""

import asyncio
import json
import logging
import aiohttp
import subprocess
import signal
import time
import threading
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

# MCP imports
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
)
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

SERVER_NAME = "xml-mcp-template"
SERVER_VERSION = "1.0.0"
SERVER_DESCRIPTION = "XML-MCP template server with Flask backend"

# Flask server configuration
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5001  # Changed from 5000 to avoid macOS Control Center conflict
FLASK_BASE_URL = f"http://{FLASK_HOST}:{FLASK_PORT}"

# ============================================================================
# MCP SERVER SETUP
# ============================================================================

server = Server(SERVER_NAME)


# ============================================================================
# FLASK SERVER MANAGER
# ============================================================================

class FlaskServerManager:
    """
    Manages the Flask server process lifecycle
    """
    
    def __init__(self, host: str = FLASK_HOST, port: int = FLASK_PORT):
        self.host = host
        self.port = port
        self.process = None
        self.base_dir = Path(__file__).parent
        
    def start_flask_server(self) -> bool:
        """
        Start the Flask server in a subprocess
        
        Returns:
            True if server started successfully, False otherwise
        """
        try:
            logger.info(f"Starting Flask server on {self.host}:{self.port}")
            
            # Check if port is already in use
            if self._is_port_in_use():
                logger.info(f"Port {self.port} already in use - Flask server may already be running")
                return True
            
            # Start Flask server subprocess - use same Python executable as current process
            import sys
            python_path = sys.executable
            cmd = [
                python_path, 
                str(self.base_dir / "run.py")
            ]
            
            logger.info(f"Using Python executable: {python_path}")
            logger.info(f"Flask server command: {' '.join(cmd)}")
            
            env = {
                **dict(os.environ),
                "FLASK_HOST": self.host,
                "FLASK_PORT": str(self.port),
                "FLASK_DEBUG": "False"
            }
            
            self.process = subprocess.Popen(
                cmd,
                cwd=self.base_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for server to start
            time.sleep(2)
            
            # Check if process is still running
            if self.process.poll() is None:
                logger.info(f"✓ Flask server started (PID: {self.process.pid})")
                
                # Wait for server to be ready
                if self._wait_for_server_ready():
                    logger.info("✓ Flask server is ready to accept connections")
                    return True
                else:
                    logger.error("Flask server started but not responding")
                    self.stop_flask_server()
                    return False
            else:
                # Process exited immediately
                stdout, stderr = self.process.communicate()
                logger.error(f"Flask server failed to start:")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting Flask server: {e}")
            return False
    
    def stop_flask_server(self):
        """Stop the Flask server subprocess"""
        if self.process:
            try:
                logger.info("Stopping Flask server...")
                
                # Try graceful shutdown first
                self.process.terminate()
                
                # Wait up to 5 seconds for graceful shutdown
                try:
                    self.process.wait(timeout=5)
                    logger.info("✓ Flask server stopped gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown failed
                    logger.warning("Force killing Flask server...")
                    self.process.kill()
                    self.process.wait()
                    logger.info("✓ Flask server force stopped")
                
                self.process = None
                
            except Exception as e:
                logger.error(f"Error stopping Flask server: {e}")
    
    def _is_port_in_use(self) -> bool:
        """Check if the Flask port is already in use"""
        import socket
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((self.host, self.port))
                return result == 0
        except:
            return False
    
    def _wait_for_server_ready(self, timeout: int = 10) -> bool:
        """
        Wait for Flask server to be ready to accept connections
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if server is ready, False if timeout
        """
        import socket
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex((self.host, self.port))
                    if result == 0:
                        return True
            except:
                pass
            
            time.sleep(0.5)
        
        return False
    
    def is_running(self) -> bool:
        """Check if Flask server process is running"""
        if self.process:
            return self.process.poll() is None
        return False


# ============================================================================
# FLASK API CLIENT
# ============================================================================

class FlaskAPIClient:
    """
    Client for communicating with Flask backend server
    """
    
    def __init__(self, base_url: str = FLASK_BASE_URL):
        self.base_url = base_url
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to Flask server"""
        url = f"{self.base_url}{endpoint}"
        session = await self._get_session()
        
        try:
            if method.upper() == "GET":
                async with session.get(url) as response:
                    result = await response.json()
            elif method.upper() == "POST":
                async with session.post(url, json=data) as response:
                    result = await response.json()
            elif method.upper() == "DELETE":
                async with session.delete(url) as response:
                    result = await response.json()
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.status >= 400:
                logger.error(f"Flask API error {response.status}: {result}")
                raise Exception(f"API error: {result.get('error', 'Unknown error')}")
            
            return result
            
        except aiohttp.ClientError as e:
            logger.error(f"Failed to connect to Flask server: {e}")
            raise Exception("Flask server not available. Please start the Flask server first.")
    
    async def analyze_input(self, content: str, input_type: str = "text", options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call Flask /api/analyze endpoint"""
        data = {
            "content": content,
            "input_type": input_type,
            "options": options or {}
        }
        return await self._make_request("POST", "/api/analyze", data)
    
    async def generate_xml(self, analysis: Dict[str, Any], output_id: str, template: str = "default", options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call Flask /api/generate endpoint"""
        data = {
            "analysis": analysis,
            "output_id": output_id,
            "template": template,
            "options": options or {}
        }
        return await self._make_request("POST", "/api/generate", data)
    
    async def process_complete(self, content: str, output_id: str, input_type: str = "text", template: str = "default", options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call Flask /api/process endpoint"""
        data = {
            "content": content,
            "output_id": output_id,
            "input_type": input_type,
            "template": template,
            "options": options or {}
        }
        return await self._make_request("POST", "/api/process", data)
    
    async def get_status(self, processing_id: str) -> Dict[str, Any]:
        """Call Flask /api/status endpoint"""
        return await self._make_request("GET", f"/api/status/{processing_id}")
    
    async def list_data(self) -> Dict[str, Any]:
        """Call Flask /api/data endpoint"""
        return await self._make_request("GET", "/api/data")
    
    async def get_data(self, data_id: str) -> Dict[str, Any]:
        """Call Flask /api/data/{id} endpoint"""
        return await self._make_request("GET", f"/api/data/{data_id}")
    
    async def delete_data(self, data_id: str) -> Dict[str, Any]:
        """Call Flask /api/data/{id} DELETE endpoint"""
        return await self._make_request("DELETE", f"/api/data/{data_id}")
    
    async def list_templates(self) -> Dict[str, Any]:
        """Call Flask /api/templates endpoint"""
        return await self._make_request("GET", "/api/templates")
    
    async def health_check(self) -> Dict[str, Any]:
        """Call Flask /health endpoint"""
        return await self._make_request("GET", "/health")
    
    async def close(self):
        """Close the session"""
        if self.session:
            try:
                await self.session.close()
                logger.info("✓ HTTP session closed successfully")
            except Exception as e:
                logger.warning(f"Error closing HTTP session: {e}")
            finally:
                self.session = None


# ============================================================================
# MCP TOOLS DEFINITION
# ============================================================================

# Initialize Flask server manager and API client
flask_manager = FlaskServerManager()
flask_client = FlaskAPIClient()


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """Define available MCP tools"""
    return [
        types.Tool(
                name="analyze_input",
                description="Analyze input content and extract information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Content to analyze"
                        },
                        "input_type": {
                            "type": "string",
                            "description": "Type of input (text, markdown, json, etc.)",
                            "default": "text"
                        }
                    },
                    "required": ["content"]
                }
            ),
            types.Tool(
                name="generate_xml",
                description="Generate XML output from analysis results",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "analysis": {
                            "type": "object",
                            "description": "Analysis results"
                        },
                        "output_id": {
                            "type": "string",
                            "description": "Unique identifier for output"
                        },
                        "template": {
                            "type": "string",
                            "description": "XML template to use (default, task_packet, analysis_report)",
                            "default": "default"
                        },
                        "options": {
                            "type": "object",
                            "description": "Additional generation options",
                            "default": {}
                        }
                    },
                    "required": ["analysis", "output_id"]
                }
            ),
            types.Tool(
                name="process_input",
                description="Complete workflow: analyze input and generate XML",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Content to process"
                        },
                        "input_type": {
                            "type": "string",
                            "description": "Type of input",
                            "default": "text"
                        },
                        "output_id": {
                            "type": "string",
                            "description": "Unique identifier for output"
                        },
                        "template": {
                            "type": "string",
                            "description": "XML template to use",
                            "default": "default"
                        },
                        "options": {
                            "type": "object",
                            "description": "Processing options",
                            "default": {}
                        }
                    },
                    "required": ["content", "output_id"]
                }
            ),
            types.Tool(
                name="get_status",
                description="Get processing status by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "processing_id": {"type": "string"}
                    },
                    "required": ["processing_id"]
                }
            ),
            types.Tool(
                name="list_data",
                description="List all saved data entries",
                inputSchema={"type": "object", "properties": {}}
            ),
            types.Tool(
                name="get_data",
                description="Get data by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "data_id": {"type": "string"}
                    },
                    "required": ["data_id"]
                }
            ),
            types.Tool(
                name="delete_data",
                description="Delete data by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "data_id": {"type": "string"}
                    },
                    "required": ["data_id"]
                }
            ),
            types.Tool(
                name="list_templates",
                description="List available XML templates",
                inputSchema={"type": "object", "properties": {}}
            ),
            types.Tool(
                name="health_check",
                description="Check Flask server health",
                inputSchema={"type": "object", "properties": {}}
            )
        ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls by delegating to Flask server"""
    try:
        if name == "analyze_input":
            content = arguments["content"]
            input_type = arguments.get("input_type", "text")
            options = arguments.get("options", {})
            
            result = await flask_client.analyze_input(content, input_type, options)
            
            if result.get("success"):
                return [types.TextContent(
                    type="text", text=json.dumps(result["analysis"], indent=2)
                )]
            else:
                raise Exception(result.get("error", "Analysis failed"))
        
        elif name == "generate_xml":
            analysis = arguments["analysis"]
            output_id = arguments["output_id"]
            template = arguments.get("template", "default")
            options = arguments.get("options", {})
            
            result = await flask_client.generate_xml(analysis, output_id, template, options)
            
            if result.get("success"):
                return [types.TextContent(
                    type="text", text=result["xml_output"]
                )]
            else:
                raise Exception(result.get("error", "XML generation failed"))
        
        elif name == "process_input":
            content = arguments["content"]
            input_type = arguments.get("input_type", "text")
            output_id = arguments["output_id"]
            template = arguments.get("template", "default")
            options = arguments.get("options", {})
            
            result = await flask_client.process_complete(content, output_id, input_type, template, options)
            
            if result.get("success"):
                return [types.TextContent(
                    type="text", text=json.dumps(result, indent=2)
                )]
            else:
                raise Exception(result.get("error", "Processing failed"))
        
        elif name == "get_status":
            processing_id = arguments["processing_id"]
            
            result = await flask_client.get_status(processing_id)
            
            if result.get("success"):
                return [types.TextContent(
                    type="text", text=json.dumps(result, indent=2)
                )]
            else:
                raise Exception(result.get("error", "Status check failed"))
        
        elif name == "list_data":
            result = await flask_client.list_data()
            
            if result.get("success"):
                return [types.TextContent(
                    type="text", text=json.dumps(result["data"], indent=2)
                )]
            else:
                raise Exception(result.get("error", "Data listing failed"))
        
        elif name == "get_data":
            data_id = arguments["data_id"]
            
            result = await flask_client.get_data(data_id)
            
            if result.get("success"):
                return [types.TextContent(
                    type="text", text=json.dumps(result["data"], indent=2)
                )]
            else:
                raise Exception(result.get("error", f"Data {data_id} not found"))
        
        elif name == "delete_data":
            data_id = arguments["data_id"]
            
            result = await flask_client.delete_data(data_id)
            
            if result.get("success"):
                return [types.TextContent(
                    type="text", text=result["message"]
                )]
            else:
                raise Exception(result.get("error", f"Failed to delete {data_id}"))
        
        elif name == "list_templates":
            result = await flask_client.list_templates()
            
            if result.get("success"):
                return [types.TextContent(
                    type="text", text=json.dumps(result["templates"], indent=2)
                )]
            else:
                raise Exception(result.get("error", "Template listing failed"))
        
        elif name == "health_check":
            result = await flask_client.health_check()
            
            return [types.TextContent(
                type="text", text=json.dumps(result, indent=2))]
        
        else:
            return [types.TextContent(
                type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error in {name}: {e}")
        logger.error(f"Full traceback: {error_details}")
        return [types.TextContent(
            type="text", text=f"Error in {name}: {str(e)}"
        )]


# ============================================================================
# SERVER STARTUP
# ============================================================================

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        flask_manager.stop_flask_server()
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Main server entry point"""
    logger.info(f"Starting {SERVER_NAME} v{SERVER_VERSION}")
    logger.info("🚀 Launching integrated MCP + Flask server architecture")
    
    # Setup signal handlers for graceful shutdown
    setup_signal_handlers()
    
    # Step 1: Start Flask server
    logger.info("📦 Starting Flask backend server...")
    if flask_manager.start_flask_server():
        logger.info(f"✓ Flask server running on {FLASK_BASE_URL}")
    else:
        logger.error("❌ Failed to start Flask server")
        logger.error("Cannot proceed without Flask backend")
        return
    
    # Step 2: Test Flask server connection
    max_retries = 5
    for attempt in range(max_retries):
        try:
            await flask_client.health_check()
            logger.info("✓ Flask server health check passed")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Flask health check failed (attempt {attempt + 1}/{max_retries}), retrying...")
                await asyncio.sleep(1)
            else:
                logger.error(f"❌ Flask server health check failed after {max_retries} attempts: {e}")
                flask_manager.stop_flask_server()
                return
    
    # Step 3: Start MCP server
    logger.info("🔗 Starting MCP server...")
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("✓ MCP server ready - both servers running successfully")
            logger.info("🎉 System ready for Claude integration!")
            
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=SERVER_NAME,
                    server_version=SERVER_VERSION,
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        import traceback
        logger.error(f"MCP server error: {type(e).__name__}: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Handle TaskGroup exceptions specifically
        if hasattr(e, 'exceptions'):
            logger.error("TaskGroup sub-exceptions:")
            for i, exc in enumerate(e.exceptions):
                logger.error(f"  {i+1}. {type(exc).__name__}: {exc}")
        
        # Handle ExceptionGroup (Python 3.11+)
        if str(type(e)).find('ExceptionGroup') != -1:
            logger.error("Exception group detected - this may be an asyncio TaskGroup error")
    finally:
        # Clean up
        logger.info("🛑 Shutting down servers...")
        
        # Give a moment for any pending requests to complete
        try:
            await asyncio.sleep(0.5)
        except:
            pass
        
        # Close HTTP client session
        try:
            await flask_client.close()
        except Exception as e:
            logger.warning(f"Error closing Flask client: {e}")
        
        # Stop Flask server
        try:
            flask_manager.stop_flask_server()
        except Exception as e:
            logger.warning(f"Error stopping Flask server: {e}")
        
        logger.info("✓ All servers stopped - goodbye!")


if __name__ == "__main__":
    asyncio.run(main())