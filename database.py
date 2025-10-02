"""
SQLite Database Setup for BIM Execution Plan - Thread-Safe Version
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List
import os

DATABASE_NAME = 'bim_execution_plans.db'


class BIMDatabase:
    def __init__(self, db_path: str = DATABASE_NAME):
        """Initialize database and create tables if they don't exist."""
        self.db_path = db_path
        # Create tables on initialization
        conn = self.get_connection()
        self.create_tables(conn)
        conn.close()

    def get_connection(self):
        """Get a new database connection for each request (thread-safe)."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn

    def create_tables(self, conn):
        """Create all necessary tables for storing BIM Execution Plan data."""
        cursor = conn.cursor()

        # Main BEP Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                owner_name TEXT NOT NULL,
                project_description TEXT,
                delivery_method TEXT,
                facility_type TEXT,
                project_value REAL,
                project_area REAL,
                project_location TEXT,
                standard_used TEXT,
                project_start_date DATE,
                project_end_date DATE,
                design_phase_end DATE,
                construction_start DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Project Contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                organization TEXT NOT NULL,
                role TEXT NOT NULL,
                contact_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        ''')

        # BIM Uses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bim_uses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                bim_use TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        ''')

        # Software table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS software (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                software_name TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        ''')

        # BIM Roles & Responsibilities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bim_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                bim_manager TEXT,
                bim_coordinator TEXT,
                model_authors TEXT,
                additional_roles TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        ''')

        # Collaboration Details table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collaboration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                collaboration_platform TEXT NOT NULL,
                meeting_schedule TEXT NOT NULL,
                file_naming_convention TEXT NOT NULL,
                communication_protocol TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        ''')

        # Technology Requirements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS technology (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                file_formats TEXT NOT NULL,
                coordinate_system TEXT NOT NULL,
                additional_software TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        ''')

        # Model Management table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_management (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                lod_requirements TEXT NOT NULL,
                model_structure TEXT NOT NULL,
                origin_point TEXT,
                modeling_standards TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        ''')

        # Quality Control table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_control (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                qa_process TEXT NOT NULL,
                clash_detection_schedule TEXT NOT NULL,
                issue_resolution TEXT,
                model_audit TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        ''')

        # Deliverables & Risk table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deliverables_risk (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                project_deliverables TEXT NOT NULL,
                project_goals TEXT,
                key_milestones TEXT,
                data_handover TEXT,
                risk_register TEXT,
                additional_notes TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        ''')

        # Create indexes for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_project_name ON projects(project_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_project ON contacts(project_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bim_uses_project ON bim_uses(project_id)')

        conn.commit()

    def insert_project(self, data: Dict) -> int:
        """Insert a complete BIM Execution Plan project."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Insert main project data
            cursor.execute('''
                INSERT INTO projects (
                    project_name, owner_name, project_description, delivery_method,
                    facility_type, project_value, project_area, project_location,
                    standard_used, project_start_date, project_end_date,
                    design_phase_end, construction_start
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('projectName'),
                data.get('ownerName'),
                data.get('projectDescription'),
                data.get('deliveryMethod'),
                data.get('facilityType'),
                data.get('projectValue'),
                data.get('projectArea'),
                data.get('projectLocation'),
                data.get('standardUsed'),
                data.get('projectStartDate'),
                data.get('projectEndDate'),
                data.get('designPhaseEnd'),
                data.get('constructionStart')
            ))

            project_id = cursor.lastrowid

            # Insert contacts
            contact_num = 1
            while f'contactOrg{contact_num}' in data:
                cursor.execute('''
                    INSERT INTO contacts (project_id, organization, role, contact_name, email, phone)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    project_id,
                    data.get(f'contactOrg{contact_num}'),
                    data.get(f'contactRole{contact_num}'),
                    data.get(f'contactName{contact_num}'),
                    data.get(f'contactEmail{contact_num}'),
                    data.get(f'contactPhone{contact_num}')
                ))
                contact_num += 1

            # Insert BIM uses
            if 'bimUse' in data and isinstance(data['bimUse'], list):
                for bim_use in data['bimUse']:
                    cursor.execute('''
                        INSERT INTO bim_uses (project_id, bim_use)
                        VALUES (?, ?)
                    ''', (project_id, bim_use))

            # Insert software
            if 'software' in data and isinstance(data['software'], list):
                for software in data['software']:
                    cursor.execute('''
                        INSERT INTO software (project_id, software_name)
                        VALUES (?, ?)
                    ''', (project_id, software))

            # Insert BIM roles
            cursor.execute('''
                INSERT INTO bim_roles (project_id, bim_manager, bim_coordinator, model_authors, additional_roles)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                project_id,
                data.get('bimManager'),
                data.get('bimCoordinator'),
                data.get('modelAuthors'),
                data.get('additionalRoles')
            ))

            # Insert collaboration details
            cursor.execute('''
                INSERT INTO collaboration (project_id, collaboration_platform, meeting_schedule,
                                          file_naming_convention, communication_protocol)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                project_id,
                data.get('collaborationPlatform'),
                data.get('meetingSchedule'),
                data.get('fileNamingConvention'),
                data.get('communicationProtocol')
            ))

            # Insert technology details
            cursor.execute('''
                INSERT INTO technology (project_id, file_formats, coordinate_system, additional_software)
                VALUES (?, ?, ?, ?)
            ''', (
                project_id,
                data.get('fileFormats'),
                data.get('coordinateSystem'),
                data.get('additionalSoftware')
            ))

            # Insert model management
            cursor.execute('''
                INSERT INTO model_management (project_id, lod_requirements, model_structure,
                                             origin_point, modeling_standards)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                project_id,
                data.get('lodRequirements'),
                data.get('modelStructure'),
                data.get('originPoint'),
                data.get('modelingStandards')
            ))

            # Insert quality control
            cursor.execute('''
                INSERT INTO quality_control (project_id, qa_process, clash_detection_schedule,
                                            issue_resolution, model_audit)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                project_id,
                data.get('qaProcess'),
                data.get('clashDetection'),
                data.get('issueResolution'),
                data.get('modelAudit')
            ))

            # Insert deliverables and risk
            cursor.execute('''
                INSERT INTO deliverables_risk (project_id, project_deliverables, project_goals,
                                              key_milestones, data_handover, risk_register, additional_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                project_id,
                data.get('projectDeliverables'),
                data.get('projectGoals'),
                data.get('keyMilestones'),
                data.get('dataHandover'),
                data.get('riskRegister'),
                data.get('additionalNotes')
            ))

            conn.commit()
            return project_id

        finally:
            conn.close()

    def get_project(self, project_id: int) -> Optional[Dict]:
        """Retrieve a complete BIM Execution Plan project by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Get main project data
            cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
            project = cursor.fetchone()

            if not project:
                return None

            project_data = dict(project)

            # Get contacts
            cursor.execute('SELECT * FROM contacts WHERE project_id = ?', (project_id,))
            project_data['contacts'] = [dict(row) for row in cursor.fetchall()]

            # Get BIM uses
            cursor.execute('SELECT bim_use FROM bim_uses WHERE project_id = ?', (project_id,))
            project_data['bim_uses'] = [row['bim_use'] for row in cursor.fetchall()]

            # Get software
            cursor.execute('SELECT software_name FROM software WHERE project_id = ?', (project_id,))
            project_data['software'] = [row['software_name'] for row in cursor.fetchall()]

            # Get other related data
            cursor.execute('SELECT * FROM bim_roles WHERE project_id = ?', (project_id,))
            bim_roles = cursor.fetchone()
            if bim_roles:
                project_data['bim_roles'] = dict(bim_roles)

            cursor.execute('SELECT * FROM collaboration WHERE project_id = ?', (project_id,))
            collaboration = cursor.fetchone()
            if collaboration:
                project_data['collaboration'] = dict(collaboration)

            cursor.execute('SELECT * FROM technology WHERE project_id = ?', (project_id,))
            technology = cursor.fetchone()
            if technology:
                project_data['technology'] = dict(technology)

            cursor.execute('SELECT * FROM model_management WHERE project_id = ?', (project_id,))
            model_mgmt = cursor.fetchone()
            if model_mgmt:
                project_data['model_management'] = dict(model_mgmt)

            cursor.execute('SELECT * FROM quality_control WHERE project_id = ?', (project_id,))
            qc = cursor.fetchone()
            if qc:
                project_data['quality_control'] = dict(qc)

            cursor.execute('SELECT * FROM deliverables_risk WHERE project_id = ?', (project_id,))
            deliverables = cursor.fetchone()
            if deliverables:
                project_data['deliverables_risk'] = dict(deliverables)

            return project_data

        finally:
            conn.close()

    def get_all_projects(self) -> List[Dict]:
        """Retrieve all projects (summary view)."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id, project_name, owner_name, facility_type,
                       project_start_date, created_at
                FROM projects
                ORDER BY created_at DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]

        finally:
            conn.close()

    def delete_project(self, project_id: int) -> bool:
        """Delete a project and all related data (CASCADE)."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
            conn.commit()
            return cursor.rowcount > 0

        finally:
            conn.close()

    def search_projects(self, search_term: str) -> List[Dict]:
        """Search projects by name or owner."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id, project_name, owner_name, facility_type,
                       project_start_date, created_at
                FROM projects
                WHERE project_name LIKE ? OR owner_name LIKE ?
                ORDER BY created_at DESC
            ''', (f'%{search_term}%', f'%{search_term}%'))
            return [dict(row) for row in cursor.fetchall()]

        finally:
            conn.close()


def initialize_database():
    """Initialize the database and return the database instance."""
    db = BIMDatabase()
    print(f"Database initialized: {db.db_path}")
    return db


if __name__ == '__main__':
    # Initialize database and create tables
    db = initialize_database()
    print("Database tables created successfully!")
    print(f"Database location: {os.path.abspath(db.db_path)}")
