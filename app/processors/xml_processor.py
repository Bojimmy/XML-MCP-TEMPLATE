"""
XML Processor for XML-MCP Template

This module handles the core XML processing logic including:
- Input content analysis
- XML output generation
- Template management
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from lxml import etree

logger = logging.getLogger(__name__)


class XMLProcessor:
    """
    Core XML processing engine
    
    Handles analysis of input content and generation of structured XML outputs.
    Can be extended for domain-specific processing needs.
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize XML processor
        
        Args:
            templates_dir: Directory containing XML templates
        """
        self.base_dir = Path(__file__).parent.parent.parent
        self.schemas_dir = self.base_dir / "schemas"
        self.templates_dir = templates_dir or self.schemas_dir
        
        # Available templates
        self.templates = {
            'default': 'template-schema.xml',
            'task_packet': 'taskpacket-schema.xml',
            'analysis_report': 'analysis-schema.xml'
        }
        
        logger.info(f"XMLProcessor initialized with schemas: {self.schemas_dir}")
    
    def analyze_input(self, content: str, input_type: str = "text", options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze input content and extract structured information
        
        Args:
            content: Raw input content to analyze
            input_type: Type of input (text, markdown, json, etc.)
            options: Additional processing options
            
        Returns:
            Dictionary containing analysis results
        """
        if options is None:
            options = {}
        
        logger.info(f"Analyzing {input_type} content ({len(content)} chars)")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "input_type": input_type,
            "content_length": len(content),
            "word_count": len(content.split()),
            "basic_stats": self._get_basic_stats(content),
            "structure": self._analyze_structure(content, input_type),
            "metadata": self._extract_metadata(content, input_type),
            "complexity_score": self._calculate_complexity(content, input_type),
            "processing_options": options
        }
        
        # Add type-specific analysis
        if input_type == "markdown":
            analysis["markdown_features"] = self._analyze_markdown(content)
        elif input_type == "json":
            analysis["json_structure"] = self._analyze_json(content)
        elif input_type == "xml":
            analysis["xml_structure"] = self._analyze_xml(content)
        
        logger.info(f"Analysis complete: {analysis['word_count']} words, complexity: {analysis['complexity_score']}")
        return analysis
    
    def generate_xml_output(self, analysis: Dict[str, Any], output_id: str, 
                          template: str = "default", options: Dict[str, Any] = None) -> str:
        """
        Generate XML output based on analysis results
        
        Args:
            analysis: Analysis results from analyze_input()
            output_id: Unique identifier for this output
            template: Template to use for XML generation
            options: Additional generation options
            
        Returns:
            XML string formatted according to template
        """
        if options is None:
            options = {}
        
        logger.info(f"Generating XML output: {output_id}, template: {template}")
        
        # Create root element based on template
        if template == "task_packet":
            root = self._create_task_packet_xml(analysis, output_id, options)
        elif template == "analysis_report":
            root = self._create_analysis_report_xml(analysis, output_id, options)
        else:
            root = self._create_default_xml(analysis, output_id, options)
        
        # Convert to string
        xml_output = etree.tostring(root, pretty_print=True, encoding="unicode")
        
        logger.info(f"XML generation complete: {len(xml_output)} characters")
        return xml_output
    
    def list_templates(self) -> List[Dict[str, str]]:
        """
        List available XML templates
        
        Returns:
            List of template information
        """
        template_list = []
        for name, schema_file in self.templates.items():
            template_info = {
                "name": name,
                "schema_file": schema_file,
                "description": self._get_template_description(name)
            }
            template_list.append(template_info)
        
        return template_list
    
    def _get_basic_stats(self, content: str) -> Dict[str, int]:
        """Get basic statistics about the content"""
        lines = content.split('\n')
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        
        return {
            "lines": len(lines),
            "characters": len(content),
            "characters_no_spaces": len(content.replace(' ', '')),
            "words": len(content.split()),
            "paragraphs": len(paragraphs),
            "sentences": content.count('.') + content.count('!') + content.count('?')
        }
    
    def _analyze_structure(self, content: str, input_type: str) -> Dict[str, List[str]]:
        """Analyze content structure based on input type"""
        structure = {"sections": [], "lists": [], "code_blocks": [], "links": []}
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Headers/sections
            if line.startswith('#'):
                structure["sections"].append(line)
            elif line.startswith(('-', '*', '+', '1.', '2.', '3.')):
                structure["lists"].append(line)
            elif line.startswith('```') or line.startswith('    '):
                structure["code_blocks"].append(line)
            elif '[' in line and '](' in line:
                structure["links"].append(line)
        
        return structure
    
    def _extract_metadata(self, content: str, input_type: str) -> Dict[str, str]:
        """Extract metadata from content"""
        metadata = {}
        
        # Look for key-value pairs in the first few lines
        lines = content.split('\n')[:20]
        
        for line in lines:
            if ':' in line and not line.strip().startswith('#'):
                parts = line.split(':', 1)
                if len(parts) == 2 and len(parts[0]) < 50:
                    key = parts[0].strip().lower().replace(' ', '_')
                    value = parts[1].strip()
                    if value and len(value) < 200:
                        metadata[key] = value
        
        return metadata
    
    def _calculate_complexity(self, content: str, input_type: str) -> int:
        """Calculate complexity score based on content analysis"""
        score = 0
        content_lower = content.lower()
        
        # Length-based complexity
        word_count = len(content.split())
        if word_count > 1000:
            score += 3
        elif word_count > 500:
            score += 2
        elif word_count > 200:
            score += 1
        
        # Structure complexity
        lines = content.split('\n')
        sections = len([line for line in lines if line.strip().startswith('#')])
        lists = len([line for line in lines if line.strip().startswith(('-', '*', '+'))])
        
        score += min(sections, 5)  # Cap section contribution
        score += min(lists // 3, 3)  # Every 3 list items adds 1 point
        
        # Content complexity keywords
        complexity_keywords = {
            'complex': 1, 'integrate': 1, 'system': 1, 'process': 1,
            'workflow': 2, 'automation': 2, 'api': 2, 'database': 2,
            'security': 2, 'performance': 2, 'scalability': 3,
            'architecture': 2, 'framework': 1, 'algorithm': 2
        }
        
        for keyword, weight in complexity_keywords.items():
            score += content_lower.count(keyword) * weight
        
        return min(score, 20)  # Cap at 20
    
    def _analyze_markdown(self, content: str) -> Dict[str, Any]:
        """Analyze markdown-specific features"""
        return {
            "headers": {
                "h1": content.count('\n# '),
                "h2": content.count('\n## '),
                "h3": content.count('\n### '),
                "total": len([line for line in content.split('\n') if line.startswith('#')])
            },
            "formatting": {
                "bold": content.count('**'),
                "italic": content.count('*') - content.count('**') * 2,
                "code_inline": content.count('`') - content.count('```') * 3,
                "code_blocks": content.count('```') // 2
            },
            "links": content.count(']('),
            "images": content.count('!['),
            "tables": content.count('|') > 2
        }
    
    def _analyze_json(self, content: str) -> Dict[str, Any]:
        """Analyze JSON structure"""
        try:
            data = json.loads(content)
            return {
                "valid": True,
                "type": type(data).__name__,
                "keys": list(data.keys()) if isinstance(data, dict) else None,
                "length": len(data) if isinstance(data, (list, dict)) else None,
                "depth": self._get_json_depth(data),
                "has_arrays": self._has_arrays(data),
                "has_objects": self._has_objects(data)
            }
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def _analyze_xml(self, content: str) -> Dict[str, Any]:
        """Analyze XML structure"""
        try:
            root = etree.fromstring(content)
            return {
                "valid": True,
                "root_tag": root.tag,
                "elements": len(root.xpath('//*')),
                "attributes": len(root.xpath('//@*')),
                "depth": self._get_xml_depth(root),
                "namespaces": list(root.nsmap.keys()) if root.nsmap else []
            }
        except etree.XMLSyntaxError as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def _get_json_depth(self, obj, depth=0):
        """Calculate JSON nesting depth"""
        if isinstance(obj, dict):
            return max([self._get_json_depth(v, depth + 1) for v in obj.values()], default=depth)
        elif isinstance(obj, list):
            return max([self._get_json_depth(item, depth + 1) for item in obj], default=depth)
        return depth
    
    def _get_xml_depth(self, element, depth=0):
        """Calculate XML nesting depth"""
        if len(element) == 0:
            return depth
        return max([self._get_xml_depth(child, depth + 1) for child in element])
    
    def _has_arrays(self, obj):
        """Check if JSON contains arrays"""
        if isinstance(obj, list):
            return True
        elif isinstance(obj, dict):
            return any(self._has_arrays(v) for v in obj.values())
        return False
    
    def _has_objects(self, obj):
        """Check if JSON contains objects"""
        if isinstance(obj, dict):
            return True
        elif isinstance(obj, list):
            return any(self._has_objects(item) for item in obj)
        return False
    
    def _create_default_xml(self, analysis: Dict[str, Any], output_id: str, options: Dict[str, Any]) -> etree.Element:
        """Create default XML output"""
        root = etree.Element("Output")
        root.set("id", output_id)
        root.set("generated", datetime.now().isoformat())
        root.set("template", "default")
        
        # Metadata
        metadata = etree.SubElement(root, "Metadata")
        etree.SubElement(metadata, "InputType").text = analysis.get("input_type", "unknown")
        etree.SubElement(metadata, "WordCount").text = str(analysis.get("word_count", 0))
        etree.SubElement(metadata, "ComplexityScore").text = str(analysis.get("complexity_score", 0))
        
        # Analysis
        analysis_elem = etree.SubElement(root, "Analysis")
        self._add_analysis_data(analysis_elem, analysis)
        
        return root
    
    def _create_task_packet_xml(self, analysis: Dict[str, Any], output_id: str, options: Dict[str, Any]) -> etree.Element:
        """Create task packet XML output"""
        root = etree.Element("TaskPacket")
        root.set("id", output_id)
        root.set("generated", datetime.now().isoformat())
        root.set("template", "task_packet")
        
        # Metadata
        metadata = etree.SubElement(root, "Metadata")
        etree.SubElement(metadata, "ComplexityScore").text = str(analysis.get("complexity_score", 0))
        etree.SubElement(metadata, "EstimatedEffort").text = self._estimate_effort(analysis)
        
        # Tasks (generated from analysis)
        tasks = etree.SubElement(root, "Tasks")
        self._generate_tasks(tasks, analysis)
        
        return root
    
    def _create_analysis_report_xml(self, analysis: Dict[str, Any], output_id: str, options: Dict[str, Any]) -> etree.Element:
        """Create analysis report XML output"""
        root = etree.Element("AnalysisReport")
        root.set("id", output_id)
        root.set("generated", datetime.now().isoformat())
        root.set("template", "analysis_report")
        
        # Summary
        summary = etree.SubElement(root, "Summary")
        self._add_analysis_summary(summary, analysis)
        
        # Detailed analysis
        details = etree.SubElement(root, "DetailedAnalysis")
        self._add_analysis_data(details, analysis)
        
        return root
    
    def _add_analysis_data(self, parent: etree.Element, analysis: Dict[str, Any]):
        """Add analysis data to XML element"""
        for key, value in analysis.items():
            if key in ["timestamp", "processing_options"]:
                continue
                
            elem = etree.SubElement(parent, key.title().replace("_", ""))
            
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    sub_elem = etree.SubElement(elem, sub_key.title().replace("_", ""))
                    sub_elem.text = str(sub_value)
            elif isinstance(value, list):
                for item in value[:10]:  # Limit to 10 items
                    item_elem = etree.SubElement(elem, "Item")
                    item_elem.text = str(item)
            else:
                elem.text = str(value)
    
    def _add_analysis_summary(self, parent: etree.Element, analysis: Dict[str, Any]):
        """Add analysis summary to XML element"""
        etree.SubElement(parent, "WordCount").text = str(analysis.get("word_count", 0))
        etree.SubElement(parent, "InputType").text = analysis.get("input_type", "unknown")
        etree.SubElement(parent, "ComplexityScore").text = str(analysis.get("complexity_score", 0))
        
        # Structure summary
        structure = analysis.get("structure", {})
        etree.SubElement(parent, "SectionCount").text = str(len(structure.get("sections", [])))
        etree.SubElement(parent, "ListCount").text = str(len(structure.get("lists", [])))
    
    def _generate_tasks(self, parent: etree.Element, analysis: Dict[str, Any]):
        """Generate tasks based on analysis"""
        complexity = analysis.get("complexity_score", 0)
        sections = analysis.get("structure", {}).get("sections", [])
        
        # Generate basic tasks
        tasks = [
            {"title": "Analysis and Planning", "priority": "high", "hours": 4},
            {"title": "Implementation", "priority": "medium", "hours": 8},
            {"title": "Testing and Review", "priority": "medium", "hours": 4}
        ]
        
        # Add section-based tasks
        for i, section in enumerate(sections[:5]):  # Limit to 5 sections
            tasks.append({
                "title": f"Process: {section[:50]}",
                "priority": "medium",
                "hours": max(2, complexity // 3)
            })
        
        # Create task elements
        for i, task in enumerate(tasks, 1):
            task_elem = etree.SubElement(parent, "Task")
            task_elem.set("id", f"task_{i}")
            
            etree.SubElement(task_elem, "Title").text = task["title"]
            etree.SubElement(task_elem, "Priority").text = task["priority"]
            etree.SubElement(task_elem, "EstimatedHours").text = str(task["hours"])
    
    def _estimate_effort(self, analysis: Dict[str, Any]) -> str:
        """Estimate effort based on complexity"""
        complexity = analysis.get("complexity_score", 0)
        
        if complexity <= 5:
            return "Low (1-2 days)"
        elif complexity <= 10:
            return "Medium (3-5 days)"
        elif complexity <= 15:
            return "High (1-2 weeks)"
        else:
            return "Very High (2+ weeks)"
    
    def _get_template_description(self, template_name: str) -> str:
        """Get description for template"""
        descriptions = {
            "default": "Generic XML output with analysis results",
            "task_packet": "Structured task breakdown with effort estimates",
            "analysis_report": "Detailed analysis report with summary"
        }
        return descriptions.get(template_name, "Custom template")