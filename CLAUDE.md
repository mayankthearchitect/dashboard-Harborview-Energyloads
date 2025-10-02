# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BIM (Building Information Modeling) Execution Plan web application with a Flask REST API backend and SQLite database. The application manages comprehensive 10-section BIM execution plans with features for creation, editing, export (PDF/DOCX), search, and project tracking.

## Technology Stack

- **Backend**: Flask REST API (Python 3.8+)
- **Database**: SQLite3 with normalized schema (10 related tables)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Export**: ReportLab (PDF), python-docx (DOCX)

## Development Commands

### Setup & Initialization
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize/reset database
python database.py
```

### Running the Application
```bash
# Start Flask server (runs on port 5001, not 5000)
python server.py

# Access application at: http://localhost:5001
```

### Testing API
```bash
# Health check
curl http://localhost:5001/api/health

# Get all projects
curl http://localhost:5001/api/projects

# Get specific project
curl http://localhost:5001/api/projects/<id>

# Search projects
curl http://localhost:5001/api/projects/search?q=searchterm
```

## Architecture

### Database Schema (database.py)

Thread-safe SQLite implementation with normalized structure:
- **Main table**: `projects` - Core project information
- **Related tables**: `contacts`, `bim_uses`, `software`, `bim_roles`, `collaboration`, `technology`, `model_management`, `quality_control`, `deliverables_risk`
- Foreign keys cascade on delete
- Uses `sqlite3.Row` for dictionary-style row access
- Connection pooling: New connection per request via `get_connection()`

Key methods in `BIMDatabase` class:
- `insert_project(data)` - Creates project with all related records
- `get_project(project_id)` - Returns complete project with all joins
- `get_all_projects()` - Returns summary view (id, name, owner, facility_type, dates)
- `update_project(project_id, data)` - Updates project (not implemented yet)
- `delete_project(project_id)` - Cascade deletes all related records
- `search_projects(search_term)` - Full-text search on name/owner

### API Structure (server.py)

Flask server with CORS enabled, runs on port 5001 (not 5000 as in README).

**Endpoints**:
- Static file serving: `/`, `/dashboard.html`, `/bim-execution-plan.html`, `/view-project.html`
- CRUD: GET/POST `/api/projects`, GET/PUT/DELETE `/api/projects/<id>`
- Search: GET `/api/projects/search?q=...`
- Export: GET `/api/projects/<id>/export/pdf` and `/export/docx`
- Stats: GET `/api/stats`

Response format: `{success: bool, data/error: ..., count: int}`

### Frontend Architecture

**Pages**:
- `dashboard.html` - Project listing, search, statistics (default route)
- `bim-execution-plan.html` - 10-section form for creating/editing BEPs
- `view-project.html` - View single project details
- `script.js` - Shared client-side logic
- `styles.css` - Global styles

**Key Features**:
- Auto-save to localStorage every 30 seconds
- Multi-step form navigation with validation
- Dynamic contact management (add/remove)
- Responsive design
- Keyboard shortcuts: Alt+Arrow for navigation

### Export System (export_utils.py)

Two exporter classes inheriting from `BEPExporter`:
- `PDFExporter` - Uses ReportLab to generate formatted PDFs
- `DOCXExporter` - Uses python-docx for Word documents

Both generate in-memory buffers returned via Flask's `send_file()`.

## Form Data Structure

The frontend sends camelCase JSON keys that map to snake_case database columns. Example:
- `projectName` → `project_name`
- `bimUse` (array) → multiple rows in `bim_uses` table
- `contactOrg1`, `contactOrg2`, etc. → multiple rows in `contacts` table

Contacts are numbered sequentially (1, 2, 3...) with fields: `contactOrg{N}`, `contactRole{N}`, `contactName{N}`, `contactEmail{N}`, `contactPhone{N}`.

## Important Notes

- Server runs on **port 5001**, not 5000 (server.py:385 differs from README)
- Database method `update_project()` is declared in server.py but not implemented in database.py
- All database operations use thread-safe connection handling
- Foreign key constraints require SQLite to be compiled with foreign key support
- localStorage draft recovery prompts user on return to form
- Export filenames include project name and current date

## Standards Compliance

Application follows:
- NIBS NBIMS-US V4
- ISO 19650
- Penn State BIM Execution Plan template structure
