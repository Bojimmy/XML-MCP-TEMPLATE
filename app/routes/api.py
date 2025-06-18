"""
API Routes for XML-MCP Template

This module defines the REST API endpoints for XML processing.
These endpoints are called by the MCP server and can also be used by web UIs.
"""

import logging
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from app.processors.xml_processor import XMLProcessor
from app.processors.data_manager import DataManager

# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize processors
xml_processor = XMLProcessor()
data_manager = DataManager()

logger = logging.getLogger(__name__)


@api_bp.route('/analyze', methods=['POST'])
def analyze_input():
    """
    Analyze input content and extract structured information
    
    Expected JSON payload:
    {
        "content": "text to analyze",
        "input_type": "text|markdown|json",
        "options": {}
    }
    
    Returns:
    {
        "success": true,
        "analysis": {...},
        "processing_id": "uuid"
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        # Validate required fields
        content = data.get('content')
        if not content:
            return jsonify({'error': 'content field is required'}), 400
        
        input_type = data.get('input_type', 'text')
        options = data.get('options', {})
        
        # Generate processing ID
        processing_id = str(uuid.uuid4())
        
        logger.info(f"Analyzing input: {processing_id}, type: {input_type}")
        
        # Perform analysis
        analysis = xml_processor.analyze_input(content, input_type, options)
        
        # Store result
        result_data = {
            'processing_id': processing_id,
            'analysis': analysis,
            'input_type': input_type,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        data_manager.store_result(processing_id, result_data)
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'processing_id': processing_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error in analyze_input: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/generate', methods=['POST'])
def generate_xml():
    """
    Generate XML output from analysis results
    
    Expected JSON payload:
    {
        "analysis": {...},
        "output_id": "unique-id",
        "template": "template-name",
        "options": {}
    }
    
    Returns:
    {
        "success": true,
        "xml_output": "xml string",
        "output_id": "unique-id"
    }
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        # Validate required fields
        analysis = data.get('analysis')
        if not analysis:
            return jsonify({'error': 'analysis field is required'}), 400
        
        output_id = data.get('output_id', str(uuid.uuid4()))
        template = data.get('template', 'default')
        options = data.get('options', {})
        
        logger.info(f"Generating XML: {output_id}, template: {template}")
        
        # Generate XML
        xml_output = xml_processor.generate_xml_output(analysis, output_id, template, options)
        
        # Store result
        result_data = {
            'output_id': output_id,
            'xml_output': xml_output,
            'analysis': analysis,
            'template': template,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        data_manager.store_result(output_id, result_data)
        
        return jsonify({
            'success': True,
            'xml_output': xml_output,
            'output_id': output_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error in generate_xml: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/process', methods=['POST'])
def process_complete():
    """
    Complete workflow: analyze input and generate XML
    
    Expected JSON payload:
    {
        "content": "text to process",
        "input_type": "text|markdown|json",
        "output_id": "unique-id",
        "template": "template-name",
        "options": {}
    }
    
    Returns:
    {
        "success": true,
        "analysis": {...},
        "xml_output": "xml string",
        "processing_id": "uuid"
    }
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        # Validate required fields
        content = data.get('content')
        if not content:
            return jsonify({'error': 'content field is required'}), 400
        
        input_type = data.get('input_type', 'text')
        output_id = data.get('output_id', str(uuid.uuid4()))
        template = data.get('template', 'default')
        options = data.get('options', {})
        
        processing_id = str(uuid.uuid4())
        
        logger.info(f"Processing complete workflow: {processing_id}")
        
        # Step 1: Analyze input
        analysis = xml_processor.analyze_input(content, input_type, options)
        
        # Step 2: Generate XML
        xml_output = xml_processor.generate_xml_output(analysis, output_id, template, options)
        
        # Store complete result
        result_data = {
            'processing_id': processing_id,
            'output_id': output_id,
            'analysis': analysis,
            'xml_output': xml_output,
            'input_type': input_type,
            'template': template,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        data_manager.store_result(processing_id, result_data)
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'xml_output': xml_output,
            'processing_id': processing_id,
            'output_id': output_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error in process_complete: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/status/<processing_id>', methods=['GET'])
def get_status(processing_id):
    """
    Get processing status by ID
    
    Returns:
    {
        "success": true,
        "status": "completed|processing|failed",
        "result": {...}
    }
    """
    try:
        result = data_manager.get_result(processing_id)
        
        if not result:
            return jsonify({
                'success': False,
                'error': 'Processing ID not found'
            }), 404
        
        return jsonify({
            'success': True,
            'status': result.get('status', 'unknown'),
            'result': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/data', methods=['GET'])
def list_data():
    """
    List all stored data entries
    
    Returns:
    {
        "success": true,
        "data": [...]
    }
    """
    try:
        data_list = data_manager.list_all()
        
        return jsonify({
            'success': True,
            'data': data_list,
            'count': len(data_list)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in list_data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/data/<data_id>', methods=['GET'])
def get_data(data_id):
    """
    Get specific data entry by ID
    
    Returns:
    {
        "success": true,
        "data": {...}
    }
    """
    try:
        data = data_manager.get_result(data_id)
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Data ID not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/data/<data_id>', methods=['DELETE'])
def delete_data(data_id):
    """
    Delete specific data entry by ID
    
    Returns:
    {
        "success": true,
        "message": "Data deleted"
    }
    """
    try:
        success = data_manager.delete_result(data_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Data ID not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Data deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in delete_data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/templates', methods=['GET'])
def list_templates():
    """
    List available XML templates
    
    Returns:
    {
        "success": true,
        "templates": [...]
    }
    """
    try:
        templates = xml_processor.list_templates()
        
        return jsonify({
            'success': True,
            'templates': templates
        }), 200
        
    except Exception as e:
        logger.error(f"Error in list_templates: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500