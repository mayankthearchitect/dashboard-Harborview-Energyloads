"""
Flask REST API Server for BIM Execution Plan
Handles CRUD operations for BIM projects
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from database import BIMDatabase
from export_utils import PDFExporter, DOCXExporter
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize database
db = BIMDatabase()


# ========================================
# API Endpoints
# ========================================

@app.route('/')
def index():
    """Serve the home page as default page."""
    return send_from_directory('.', 'index.html')


@app.route('/index.html')
def home():
    """Serve the home page."""
    return send_from_directory('.', 'index.html')


@app.route('/bim-execution-plan.html')
def create_form():
    """Serve the BEP creation form."""
    return send_from_directory('.', 'bim-execution-plan.html')


@app.route('/dashboard.html')
def dashboard():
    """Serve the dashboard page."""
    return send_from_directory('.', 'dashboard.html')


@app.route('/view-project.html')
def view_project():
    """Serve the view project page."""
    return send_from_directory('.', 'view-project.html')


@app.route('/revit-knowledge-base.html')
def revit_knowledge_base():
    """Serve the Revit Knowledge Base page."""
    return send_from_directory('.', 'revit-knowledge-base.html')


@app.route('/styles.css')
def styles():
    """Serve CSS file."""
    return send_from_directory('.', 'styles.css')


@app.route('/script.js')
def script():
    """Serve JavaScript file."""
    return send_from_directory('.', 'script.js')


@app.route('/api/projects', methods=['GET'])
def get_all_projects():
    """Get all BIM projects (summary view)."""
    try:
        projects = db.get_all_projects()
        return jsonify({
            'success': True,
            'data': projects,
            'count': len(projects)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Get a specific BIM project by ID."""
    try:
        project = db.get_project(project_id)
        if project:
            return jsonify({
                'success': True,
                'data': project
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Project not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create a new BIM Execution Plan project."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Validate required fields
        required_fields = ['projectName', 'ownerName', 'projectDescription']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]

        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Insert project into database
        project_id = db.insert_project(data)

        return jsonify({
            'success': True,
            'message': 'Project created successfully',
            'project_id': project_id
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """Update an existing BIM project."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Check if project exists
        existing_project = db.get_project(project_id)
        if not existing_project:
            return jsonify({
                'success': False,
                'error': 'Project not found'
            }), 404

        # Update project
        success = db.update_project(project_id, data)

        if success:
            return jsonify({
                'success': True,
                'message': 'Project updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update project'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a BIM project."""
    try:
        success = db.delete_project(project_id)

        if success:
            return jsonify({
                'success': True,
                'message': 'Project deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Project not found'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/projects/search', methods=['GET'])
def search_projects():
    """Search projects by name or owner."""
    try:
        search_term = request.args.get('q', '')

        if not search_term:
            return jsonify({
                'success': False,
                'error': 'Search term required'
            }), 400

        projects = db.search_projects(search_term)

        return jsonify({
            'success': True,
            'data': projects,
            'count': len(projects)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/projects/<int:project_id>/export/pdf', methods=['GET'])
def export_project_pdf(project_id):
    """Export a project as PDF."""
    try:
        # Get project data
        project = db.get_project(project_id)

        if not project:
            return jsonify({
                'success': False,
                'error': 'Project not found'
            }), 404

        # Generate PDF
        exporter = PDFExporter(project)
        pdf_buffer = exporter.generate()

        # Generate filename
        project_name = project.get('project_name', 'project').replace(' ', '_')
        filename = f"BEP_{project_name}_{datetime.now().strftime('%Y%m%d')}.pdf"

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/projects/<int:project_id>/export/docx', methods=['GET'])
def export_project_docx(project_id):
    """Export a project as DOCX."""
    try:
        # Get project data
        project = db.get_project(project_id)

        if not project:
            return jsonify({
                'success': False,
                'error': 'Project not found'
            }), 404

        # Generate DOCX
        exporter = DOCXExporter(project)
        docx_buffer = exporter.generate()

        # Generate filename
        project_name = project.get('project_name', 'project').replace(' ', '_')
        filename = f"BEP_{project_name}_{datetime.now().strftime('%Y%m%d')}.docx"

        return send_file(
            docx_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'message': 'BIM Execution Plan API is running'
    }), 200


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics."""
    try:
        projects = db.get_all_projects()

        # Calculate statistics
        total_projects = len(projects)
        facility_types = {}

        for project in projects:
            facility_type = project.get('facility_type', 'Unknown')
            facility_types[facility_type] = facility_types.get(facility_type, 0) + 1

        return jsonify({
            'success': True,
            'stats': {
                'total_projects': total_projects,
                'facility_types': facility_types
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ========================================
# Error Handlers
# ========================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# ========================================
# Application Startup
# ========================================

if __name__ == '__main__':
    print("=" * 50)
    print("BIM Execution Plan API Server")
    print("=" * 50)
    print(f"Database: {os.path.abspath(db.db_path)}")
    print("Server starting on http://localhost:5000")
    print("=" * 50)
    print("\nAvailable Endpoints:")
    print("  GET    /                          - Serve web application")
    print("  GET    /api/health                - Health check")
    print("  GET    /api/stats                 - Database statistics")
    print("  GET    /api/projects              - Get all projects")
    print("  GET    /api/projects/<id>         - Get specific project")
    print("  POST   /api/projects              - Create new project")
    print("  PUT    /api/projects/<id>         - Update project")
    print("  DELETE /api/projects/<id>         - Delete project")
    print("  GET    /api/projects/search?q=... - Search projects")
    print("=" * 50)
    print("\nPress Ctrl+C to stop the server\n")

    app.run(debug=True, host='0.0.0.0', port=5001)
