# Sample Input Document

This is a sample input document that demonstrates how the XML-MCP template processes different types of content.

## Features

The template can handle:
- Markdown formatting
- Lists and bullet points
- Headers and sections
- Plain text content

## Usage Example

To use this template:

1. Install dependencies: `pip install -r requirements.txt`
2. Run the server: `python server.py`
3. Use MCP client to call tools with this content

## Customization Points

You can customize the template for specific use cases:

- Modify the `GenericProcessor` class
- Add domain-specific analysis methods
- Update XML schema in `schemas/`
- Add custom tools in the `list_tools()` function

This sample demonstrates various content types that the analyzer will process and convert to structured XML output.