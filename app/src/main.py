"""
SaaS Customer Portal - Sample Application
A simple Flask REST API demonstrating MCSP Scenario 1 deployment
"""

import os
import logging
import json
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from prometheus_flask_exporter import PrometheusMetrics

# Import configuration
from config import Config

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app)

# Setup Prometheus metrics
metrics = PrometheusMetrics(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# In-memory storage for demo purposes (replace with actual DB in production)
items_store = {}
item_counter = 0


def get_db_connection():
    """
    Get database connection
    In production, this would connect to PostgreSQL
    """
    try:
        conn = psycopg2.connect(
            host=app.config['DB_HOST'],
            database=app.config['DB_NAME'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            port=app.config['DB_PORT']
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return None


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for Kubernetes liveness/readiness probes
    """
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'saas-customer-portal',
        'version': app.config['APP_VERSION']
    }
    
    # Check database connectivity (optional)
    if app.config.get('CHECK_DB_HEALTH', False):
        db_conn = get_db_connection()
        if db_conn:
            health_status['database'] = 'connected'
            db_conn.close()
        else:
            health_status['database'] = 'disconnected'
            health_status['status'] = 'degraded'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code


@app.route('/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check endpoint
    """
    return jsonify({
        'status': 'ready',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/info', methods=['GET'])
def app_info():
    """
    Application information endpoint
    Returns version, environment, and configuration details
    """
    info = {
        'application': 'SaaS Customer Portal',
        'version': app.config['APP_VERSION'],
        'environment': app.config['ENVIRONMENT'],
        'build_date': app.config.get('BUILD_DATE', 'unknown'),
        'git_commit': app.config.get('GIT_COMMIT', 'unknown'),
        'cluster': app.config.get('CLUSTER_NAME', 'unknown'),
        'namespace': app.config.get('NAMESPACE', 'unknown'),
        'features': {
            'database': app.config.get('DB_ENABLED', False),
            'cache': app.config.get('CACHE_ENABLED', False),
            'metrics': True,
            'cors': True
        }
    }
    return jsonify(info), 200


@app.route('/api/items', methods=['GET'])
def get_items():
    """
    Get all items
    """
    logger.info("Fetching all items")
    items_list = list(items_store.values())
    return jsonify({
        'items': items_list,
        'count': len(items_list),
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """
    Get a specific item by ID
    """
    logger.info(f"Fetching item with ID: {item_id}")
    
    if item_id not in items_store:
        return jsonify({
            'error': 'Item not found',
            'item_id': item_id
        }), 404
    
    return jsonify(items_store[item_id]), 200


@app.route('/api/items', methods=['POST'])
def create_item():
    """
    Create a new item
    """
    global item_counter
    
    if not request.json:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    data = request.json
    
    # Validate required fields
    if 'name' not in data:
        return jsonify({'error': 'Field "name" is required'}), 400
    
    item_counter += 1
    new_item = {
        'id': item_counter,
        'name': data['name'],
        'description': data.get('description', ''),
        'category': data.get('category', 'general'),
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat(),
        'status': 'active'
    }
    
    items_store[item_counter] = new_item
    logger.info(f"Created new item with ID: {item_counter}")
    
    return jsonify(new_item), 201


@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """
    Update an existing item
    """
    logger.info(f"Updating item with ID: {item_id}")
    
    if item_id not in items_store:
        return jsonify({
            'error': 'Item not found',
            'item_id': item_id
        }), 404
    
    if not request.json:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    data = request.json
    item = items_store[item_id]
    
    # Update fields
    if 'name' in data:
        item['name'] = data['name']
    if 'description' in data:
        item['description'] = data['description']
    if 'category' in data:
        item['category'] = data['category']
    if 'status' in data:
        item['status'] = data['status']
    
    item['updated_at'] = datetime.utcnow().isoformat()
    
    return jsonify(item), 200


@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """
    Delete an item
    """
    logger.info(f"Deleting item with ID: {item_id}")
    
    if item_id not in items_store:
        return jsonify({
            'error': 'Item not found',
            'item_id': item_id
        }), 404
    
    deleted_item = items_store.pop(item_id)
    
    return jsonify({
        'message': 'Item deleted successfully',
        'item': deleted_item
    }), 200


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Get application statistics
    """
    stats = {
        'total_items': len(items_store),
        'items_by_category': {},
        'items_by_status': {},
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Calculate statistics
    for item in items_store.values():
        category = item.get('category', 'unknown')
        status = item.get('status', 'unknown')
        
        stats['items_by_category'][category] = stats['items_by_category'].get(category, 0) + 1
        stats['items_by_status'][status] = stats['items_by_status'].get(status, 0) + 1
    
    return jsonify(stats), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


@app.before_request
def log_request():
    """Log incoming requests"""
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")


@app.after_request
def add_headers(response):
    """Add security headers to responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


if __name__ == '__main__':
    # Initialize with some sample data
    items_store[1] = {
        'id': 1,
        'name': 'Sample Item 1',
        'description': 'This is a sample item',
        'category': 'demo',
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat(),
        'status': 'active'
    }
    item_counter = 1
    
    logger.info(f"Starting SaaS Customer Portal v{app.config['APP_VERSION']}")
    logger.info(f"Environment: {app.config['ENVIRONMENT']}")
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 8080)),
        debug=app.config['DEBUG']
    )

# Made with Bob
