# BIM Execution Plan Web Application

A comprehensive web application for creating and managing BIM (Building Information Modeling) Execution Plans with a SQLite backend.

## Features

- **10-Section Comprehensive Form** covering all BIM Execution Plan requirements
- **SQLite Database Backend** for persistent storage
- **REST API** for CRUD operations
- **Responsive Design** - works on desktop, tablet, and mobile
- **Auto-save** functionality with draft recovery
- **Export Options** - Download as JSON, print summary
- **Search & Filter** projects
- **Multiple Contact Management**

## Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python Flask REST API
- **Database**: SQLite3
- **Standards**: Based on NIBS, ISO 19650

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the database:**
   ```bash
   python database.py
   ```

3. **Start the Flask server:**
   ```bash
   python server.py
   ```

4. **Access the application:**
   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### Creating a New BIM Execution Plan

1. Open the web application in your browser
2. Fill out the 10 sections:
   - Project Information
   - Key Project Contacts
   - Project Goals & BIM Uses
   - BIM Roles & Responsibilities
   - Project Schedule & Milestones
   - Collaboration & Communication
   - Technology & Software Requirements
   - Model Management & Standards
   - Quality Control & Validation
   - Deliverables & Risk Management
3. Use the "Next" and "Previous" buttons to navigate
4. Click "Generate BEP" to save to database
5. Download or print your BEP

### Auto-save Feature

- Form data is automatically saved to localStorage every 30 seconds
- If you close the browser and return, you'll be prompted to restore your draft

## API Endpoints

The backend provides the following REST API endpoints:

### Health Check
```
GET /api/health
```

### Projects
```
GET    /api/projects              - Get all projects
GET    /api/projects/<id>         - Get specific project
POST   /api/projects              - Create new project
PUT    /api/projects/<id>         - Update project
DELETE /api/projects/<id>         - Delete project
GET    /api/projects/search?q=... - Search projects
```

### Statistics
```
GET /api/stats - Get database statistics
```

## Database Schema

The application uses a normalized SQLite database with the following tables:

- `projects` - Main project information
- `contacts` - Project contacts
- `bim_uses` - Selected BIM uses
- `software` - Software applications
- `bim_roles` - BIM roles and responsibilities
- `collaboration` - Collaboration details
- `technology` - Technology requirements
- `model_management` - Model management settings
- `quality_control` - QC procedures
- `deliverables_risk` - Deliverables and risk management

## Project Structure

```
ClaudeCode/
├── bim-execution-plan.html    # Main HTML file
├── styles.css                  # Styling
├── script.js                   # Frontend JavaScript
├── server.py                   # Flask API server
├── database.py                 # Database setup and operations
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── bim_execution_plans.db     # SQLite database (created on first run)
```

## Development

### Running in Development Mode

The Flask server runs in debug mode by default:

```bash
python server.py
```

Changes to Python files will automatically reload the server.

### Testing the API

You can test the API using curl or any API testing tool:

```bash
# Health check
curl http://localhost:5000/api/health

# Get all projects
curl http://localhost:5000/api/projects

# Create a new project
curl -X POST http://localhost:5000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"projectName": "Test Project", "ownerName": "Test Owner", ...}'
```

## Browser Compatibility

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Standards Compliance

This application follows industry-standard BIM Execution Plan requirements based on:

- **NIBS (National Institute of Building Sciences)** - NBIMS-US V4
- **ISO 19650** - Information Management Standards
- **Penn State BIM Execution Plan** template structure

## Keyboard Shortcuts

- `Alt + Right Arrow` - Next section
- `Alt + Left Arrow` - Previous section

## Troubleshooting

### Server won't start
- Ensure port 5000 is not in use
- Check Python dependencies are installed

### Database errors
- Delete `bim_execution_plans.db` and run `python database.py` again

### Frontend can't connect to backend
- Verify the server is running on http://localhost:5000
- Check browser console for CORS errors

## License

This project is provided as-is for BIM project planning purposes.

## Support

For issues or questions, please refer to the code documentation or contact your system administrator.
