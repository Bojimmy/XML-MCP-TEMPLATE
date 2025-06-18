# XML-MCP Template with Dual Server Architecture

A reusable template for creating MCP (Model Context Protocol) servers that process inputs and generate structured XML outputs using a dual-server architecture.

## Architecture Overview

This template uses an **integrated dual-server architecture** that provides:

1. **MCP Server** (`server.py`) - Handles Claude integration and launches Flask backend
2. **Flask Server** (`run.py`) - Provides REST API for XML processing and web UI integration

### Benefits
- **Single Command Startup**: Just run `python server.py` - Flask launches automatically
- **Integrated Lifecycle**: MCP server manages Flask server startup/shutdown
- **Web Integration**: REST API endpoints available for future web UI development
- **Separation of Concerns**: MCP protocol handling separated from business logic
- **Graceful Shutdown**: Both servers stop cleanly with proper signal handling

## Directory Structure

```
XML-MCP-TEMPLATE/
├── server.py              # MCP server (connects to Flask backend)
├── run.py                 # Flask server entry point
├── requirements.txt       # Python dependencies
├── README.md              # This documentation
├── app/                   # Flask application
│   ├── __init__.py        # Flask app factory
│   ├── routes/            # API route definitions
│   │   ├── __init__.py
│   │   └── api.py         # REST API endpoints
│   └── processors/        # XML processing logic
│       ├── __init__.py
│       ├── xml_processor.py    # Core XML processing
│       └── data_manager.py     # Data storage management
├── schemas/               # XML schema definitions
│   └── template-schema.xml
├── examples/              # Sample inputs and outputs
│   ├── sample-input.md
│   └── sample-output.xml
└── storage/               # Data storage (auto-created)
    └── data.json          # TinyDB database file
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the System (Single Command)
```bash
python server.py
```

**That's it!** The MCP server will automatically:
- 🚀 Launch the Flask backend server on http://localhost:5000
- 🔗 Start the MCP server for Claude integration  
- ✅ Verify both servers are running properly
- 🎉 System ready for Claude integration!

### 3. What You'll See
```
INFO - Starting xml-mcp-template v1.0.0
INFO - 🚀 Launching integrated MCP + Flask server architecture
INFO - 📦 Starting Flask backend server...
INFO - ✓ Flask server started (PID: 12345)
INFO - ✓ Flask server is ready to accept connections
INFO - ✓ Flask server running on http://127.0.0.1:5000
INFO - ✓ Flask server health check passed
INFO - 🔗 Starting MCP server...
INFO - ✓ MCP server ready - both servers running successfully
INFO - 🎉 System ready for Claude integration!
```

### 4. Available Tools
The MCP server provides these tools for Claude:
- `analyze_input` - Analyze content and extract information
- `generate_xml` - Generate XML from analysis results  
- `process_input` - Complete workflow (analyze + generate XML)
- `get_status` - Check processing status by ID
- `list_data` - List all saved data entries
- `get_data` - Retrieve specific data by ID
- `delete_data` - Delete data by ID
- `list_templates` - List available XML templates
- `health_check` - Check Flask server health

## MCP Tools Reference

### analyze_input
Analyze input content and extract structured information.

**Parameters:**
- `content` (string, required): Content to analyze
- `input_type` (string, optional): Type of input (text, markdown, json, etc.)
- `options` (object, optional): Additional processing options

### generate_xml
Generate XML output from analysis results.

**Parameters:**
- `analysis` (object, required): Analysis results from analyze_input
- `output_id` (string, required): Unique identifier for the output
- `template` (string, optional): XML template (default, task_packet, analysis_report)
- `options` (object, optional): Additional generation options

### process_input
Complete workflow that analyzes input and generates XML in one step.

**Parameters:**
- `content` (string, required): Content to process
- `input_type` (string, optional): Type of input
- `output_id` (string, required): Unique identifier for the output
- `template` (string, optional): XML template to use
- `options` (object, optional): Processing options

### Data Management Tools
- `get_status` - Get processing status by ID
- `list_data` - List all saved data entries
- `get_data` - Retrieve data by ID
- `delete_data` - Delete data by ID

### System Tools
- `list_templates` - List available XML templates
- `health_check` - Check Flask server health

## Flask API Endpoints

The Flask server provides REST API endpoints that can be used directly or via web interfaces:

### POST /api/analyze
Analyze input content
```json
{
  "content": "text to analyze",
  "input_type": "markdown",
  "options": {}
}
```

### POST /api/generate
Generate XML from analysis
```json
{
  "analysis": {...},
  "output_id": "unique-id",
  "template": "default",
  "options": {}
}
```

### POST /api/process
Complete workflow (analyze + generate)
```json
{
  "content": "text to process",
  "input_type": "markdown", 
  "output_id": "unique-id",
  "template": "task_packet",
  "options": {}
}
```

### GET /api/status/{processing_id}
Get processing status

### GET /api/data
List all data entries

### GET /api/data/{data_id}
Get specific data entry

### DELETE /api/data/{data_id}
Delete data entry

### GET /api/templates
List available templates

### GET /health
Health check endpoint

## Customization Guide

### 1. Server Configuration
Edit configuration in both servers:

**MCP Server (`server.py`):**
```python
SERVER_NAME = "your-custom-server"
SERVER_VERSION = "1.0.0"
FLASK_HOST = "127.0.0.1"  # Change if Flask runs elsewhere
FLASK_PORT = 5000
```

**Flask Server (`run.py`):**
```python
# Environment variables or modify run.py
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000
FLASK_DEBUG = False
```

### 2. Custom XML Processing
Extend the `XMLProcessor` class in `app/processors/xml_processor.py`:

```python
class CustomXMLProcessor(XMLProcessor):
    def analyze_input(self, content: str, input_type: str, options: Dict[str, Any] = None):
        # Call parent method
        analysis = super().analyze_input(content, input_type, options)
        
        # Add custom analysis
        analysis["custom_metrics"] = self._calculate_custom_metrics(content)
        return analysis
    
    def _calculate_custom_metrics(self, content: str):
        # Your custom analysis logic
        return {"score": len(content) * 0.1}
```

### 3. Custom API Endpoints
Add new routes in `app/routes/api.py`:

```python
@api_bp.route('/custom-analysis', methods=['POST'])
def custom_analysis():
    data = request.get_json()
    # Your custom endpoint logic
    return jsonify({"success": True, "result": "custom processing"})
```

### 4. Custom MCP Tools
Add new tools to `server.py`:

```python
Tool(
    name="custom_tool",
    description="Your custom tool description",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param1"]
    }
)
```

Then handle it in `call_tool()`:
```python
elif name == "custom_tool":
    result = await flask_client._make_request("POST", "/api/custom-analysis", arguments)
    return CallToolResult(content=[TextContent(type="text", text=json.dumps(result))])
```

### 5. XML Templates
Add new templates by extending the `templates` dictionary in `xml_processor.py`:

```python
self.templates = {
    'default': 'template-schema.xml',
    'task_packet': 'taskpacket-schema.xml', 
    'analysis_report': 'analysis-schema.xml',
    'custom_template': 'custom-schema.xml'  # Add your template
}
```

### 6. Data Storage
Extend the `DataManager` class for custom storage needs:

```python
class CustomDataManager(DataManager):
    def store_with_metadata(self, data_id: str, data: Dict[str, Any], metadata: Dict[str, Any]):
        # Add custom metadata handling
        data["custom_metadata"] = metadata
        return self.store_result(data_id, data)
```

## Use Cases

This dual-server template can be adapted for:

### Project Planning & Management
- Analyze PRDs and requirements documents
- Generate task breakdowns and work packages
- Create XML-based project plans
- Track project progress and status

### Document Analysis & Processing
- Process various document formats (Markdown, JSON, XML, etc.)
- Extract key information and metadata
- Generate structured analysis reports
- Convert documents between formats

### Workflow Automation
- Parse workflow definitions
- Generate execution plans
- Track process states and status
- Create approval workflows

### Content Management
- Analyze content for structure and complexity
- Generate content templates
- Create content taxonomies
- Process content pipelines

## Example Usage

### Via MCP Tools (with Claude)
```python
# Complete workflow example
result = await call_tool("process_input", {
    "content": "# Project Requirements\n\n## Features\n- User authentication\n- Data processing\n- Report generation",
    "input_type": "markdown", 
    "output_id": "project-001",
    "template": "task_packet"
})

# Check processing status
status = await call_tool("get_status", {
    "processing_id": "project-001"
})
```

### Via REST API (for web integration)
```bash
# Start the integrated system
python server.py &        # Launches both MCP + Flask servers

# Test Flask API directly (while MCP server is running)
curl -X POST http://localhost:5000/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Sample Document\nThis is test content.",
    "input_type": "markdown",
    "output_id": "test-001",
    "template": "default"
  }'
```

## Production Deployment

### Flask Server (Production)
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"

# Or with environment configuration
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000
export FLASK_DEBUG=False
python run.py
```

### Environment Variables
```bash
# Flask configuration
export FLASK_HOST=127.0.0.1
export FLASK_PORT=5000
export FLASK_DEBUG=False
export SECRET_KEY=your-secret-key

# MCP server will automatically detect Flask server location
```

## Development & Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests (when implemented)
pytest tests/
```

### Development Mode
```bash
# Start in debug mode (Flask will run in debug mode)
export FLASK_DEBUG=True
python server.py
```

### Adding Custom Features
1. **Flask Backend**: Add processing logic in `app/processors/`
2. **API Endpoints**: Add routes in `app/routes/api.py`
3. **MCP Tools**: Add tools in `server.py`
4. **Schemas**: Update XML schemas in `schemas/`
5. **Templates**: Add XML templates for different output types

## Troubleshooting

### Common Issues

**"Flask server not available"**
- The MCP server should start Flask automatically
- Check if port 5000 is available: `lsof -i :5000`
- Try stopping and restarting: `python server.py`
- Verify FLASK_HOST and FLASK_PORT configuration

**Import errors**
- Install all dependencies: `pip install -r requirements.txt`
- Check Python version compatibility (Python 3.8+)

**XML generation errors**
- Verify lxml installation: `pip install lxml`
- Check XML schema files in `schemas/` directory

## License

This template is provided as-is for adaptation to your specific use cases.