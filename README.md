# XML-MCP Template 🚀

**A powerful XML-centric Model Context Protocol (MCP) server template for structured document processing and task generation**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

## 🎯 **XML-First Architecture**

This template is **fundamentally built around XML** as its core processing paradigm:

- **🔄 XML Input/Output** - Process and generate structured XML documents
- **📋 XML Schema Validation** - Ensure data integrity with defined schemas  
- **🏗️ XML Template Engine** - Multiple XML output formats (task packets, analysis reports)
- **🔍 XML Query & Transform** - Built-in XML parsing and manipulation
- **💾 XML Storage** - Persistent XML-based data interchange

Perfect for systems requiring **structured, validated, and interoperable** document processing!

## ✨ **Features**

### 🚀 **Integrated Dual-Server Architecture**
- **Single Command Startup** - `python server.py` launches everything
- **MCP Server** - Handles Claude integration with 9 powerful tools
- **Flask Backend** - REST API for XML processing and web integration
- **Auto-Lifecycle Management** - Seamless startup, health monitoring, graceful shutdown

### 🔧 **9 MCP Tools for Claude**
| Tool | Purpose | XML Integration |
|------|---------|----------------|
| `analyze_input` | Extract structure from documents | XML metadata extraction |
| `generate_xml` | Create XML from analysis | Template-driven XML generation |
| `process_input` | Complete analyze→XML workflow | End-to-end XML pipeline |
| `get_status` | Check processing status | XML status documents |
| `list_data` | Browse stored entries | XML data inventory |
| `get_data` | Retrieve specific data | XML document retrieval |
| `delete_data` | Remove data entries | XML record management |
| `list_templates` | Show XML templates | XML schema catalog |
| `health_check` | System health status | XML health reports |

### 📊 **XML Templates**
- **`default`** - Generic XML output with analysis results
- **`task_packet`** - Structured project breakdown with tasks, timelines, risks
- **`analysis_report`** - Detailed document analysis with metrics and recommendations

## 🚀 **Quick Start**

### 1. **Installation**
```bash
git clone https://github.com/Bojimmy/XML-MCP-TEMPLATE.git
cd XML-MCP-TEMPLATE
pip install -r requirements.txt
```

### 2. **Launch (Single Command!)**
```bash
python server.py
```

**That's it!** The system automatically:
- 🚀 Launches Flask backend on `http://localhost:5001`
- 🔗 Starts MCP server for Claude integration
- ✅ Verifies both servers are running
- 🎉 Ready for XML processing!

### 3. **Test with Mock Data**
```bash
python test_with_mock_data.py
```

## 📁 **Project Structure**

```
XML-MCP-TEMPLATE/
├── 🗂️ Core Files
│   ├── server.py              # MCP server (auto-launches Flask)
│   ├── run.py                 # Flask server entry point  
│   └── requirements.txt       # Dependencies
├── 🏗️ Application Logic
│   └── app/
│       ├── __init__.py        # Flask app factory
│       ├── routes/api.py      # REST API endpoints
│       └── processors/        # XML processing engine
│           ├── xml_processor.py    # Core XML generation
│           └── data_manager.py     # Storage management
├── 📋 XML Infrastructure  
│   └── schemas/               # XML schema definitions
│       └── template-schema.xml
├── 🎯 Examples & Testing
│   ├── examples/              # Sample documents & XML outputs
│   │   ├── sample-prd.md           # Product Requirements Doc
│   │   ├── sample-task-packet.xml  # Generated task breakdown
│   │   └── sample-analysis-report.xml # Document analysis
│   ├── test_with_mock_data.py      # Demo script
│   └── test_startup.py             # Integration tests
└── 💾 Data Storage
    └── storage/data.json           # Persistent XML data
```

## 🔗 **Claude Desktop Integration**

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "xml-mcp-template": {
      "command": "/usr/bin/python3",
      "args": ["/path/to/XML-MCP-TEMPLATE/server.py"]
    }
  }
}
```

## 🛠️ **REST API Endpoints**

The Flask backend provides XML-focused REST endpoints:

| Endpoint | Method | Purpose | XML Output |
|----------|--------|---------|------------|
| `/api/analyze` | POST | Analyze document structure | XML metadata |
| `/api/generate` | POST | Generate XML from analysis | Templated XML |
| `/api/process` | POST | Complete analyze→XML workflow | Full XML pipeline |
| `/api/templates` | GET | List available XML templates | XML template catalog |
| `/api/data` | GET | List stored XML documents | XML inventory |
| `/health` | GET | System health check | XML status report |

## 🎨 **Customization Guide**

### **1. Add Custom XML Templates**

```python
# In xml_processor.py
self.templates = {
    'default': 'template-schema.xml',
    'task_packet': 'taskpacket-schema.xml', 
    'analysis_report': 'analysis-schema.xml',
    'custom_template': 'your-schema.xml'  # Add here
}
```

### **2. Create Custom MCP Tools**

```python
# In server.py - Add to list_tools()
types.Tool(
    name="custom_xml_tool",
    description="Your custom XML processing tool",
    inputSchema={
        "type": "object",
        "properties": {
            "xml_input": {"type": "string", "description": "XML to process"}
        }
    }
)
```

### **3. Extend XML Processing**

```python
# In xml_processor.py
class CustomXMLProcessor(XMLProcessor):
    def custom_xml_transform(self, xml_content: str) -> str:
        # Your XML transformation logic
        return transformed_xml
```

## 📊 **Use Cases**

### **🏢 Enterprise Document Processing**
- Convert requirements documents to XML task breakdowns
- Generate project plans with XML-based workflows
- Create compliance-ready XML audit trails

### **🔄 System Integration**
- XML-based data exchange between systems
- Structured document transformation pipelines
- API-first XML processing for web applications

### **📋 Project Management**
- PRD analysis and XML task packet generation
- Risk assessment with XML reporting
- Timeline and milestone tracking in XML format

### **🤖 AI-Powered Document Analysis**
- Claude integration for intelligent XML generation
- Automated document structure extraction
- Smart XML template selection based on content

## 🧪 **Testing & Examples**

### **Sample Data Included:**
- 📝 **Product Requirements Document** (`sample-prd.md`) - Complete PRD for a task management app
- 📦 **Generated Task Packet** (`sample-task-packet.xml`) - Structured project breakdown
- 📊 **Analysis Report** (`sample-analysis-report.xml`) - Detailed document analysis

### **Run Tests:**
```bash
# Test integrated startup
python test_startup.py

# Test with realistic data
python test_with_mock_data.py

# Manual API testing
curl http://localhost:5001/health
```

## ⚙️ **Configuration**

### **Server Settings**
```python
# server.py
SERVER_NAME = "xml-mcp-template"
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5001  # Avoids macOS Control Center conflict
```

### **XML Processing Options**
```python
# xml_processor.py  
XML_VALIDATION = True      # Enable XML schema validation
XML_PRETTY_PRINT = True    # Format XML output
XML_ENCODING = "UTF-8"     # XML encoding standard
```

## 🚨 **Troubleshooting**

### **Common Issues:**

**"Flask server not available"**
- Check port 5001 availability: `lsof -i :5001`
- Restart: `python server.py`

**"ModuleNotFoundError: tinydb"**
- Install dependencies: `pip install -r requirements.txt`

**XML validation errors**
- Verify XML schemas in `schemas/` directory
- Check XML template syntax

### **Debug Mode:**
```bash
export FLASK_DEBUG=True
python server.py
```

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch: `git checkout -b feature/xml-enhancement`
3. Add your XML processing improvements
4. Test with mock data: `python test_with_mock_data.py`
5. Submit pull request

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.

## 🙋 **Support**

- 📚 **Documentation**: Check the `examples/` directory for sample implementations
- 🐛 **Issues**: Report bugs via GitHub Issues
- 💡 **Features**: Suggest XML processing enhancements
- 🧪 **Testing**: Use `test_with_mock_data.py` for validation

## 🌟 **Why XML-First?**

- **🏗️ Structure** - Hierarchical, validated data organization
- **🔄 Interoperability** - Universal data exchange format
- **📋 Standards** - Well-established schemas and validation
- **🎯 Templates** - Consistent, reusable output formats
- **🔍 Queryable** - XPath, XSLT, and XML processing tools
- **📊 Metadata Rich** - Preserve context and relationships

Perfect for **enterprise systems**, **compliance requirements**, and **structured data workflows**!

---

**Ready to transform your documents into structured XML workflows? 🚀**

```bash
git clone https://github.com/Bojimmy/XML-MCP-TEMPLATE.git
cd XML-MCP-TEMPLATE
python server.py
# Your XML-powered MCP server is ready! 🎉
```