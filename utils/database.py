import pandas as pd
import sqlite3
import os
import json
from datetime import datetime

class InspectionDatabase:
    """
    Class to handle storage and retrieval of inspection data
    """
    def __init__(self, db_path=":memory:"):
        """
        Initialize the database
        Args:
            db_path: Path to the database file, defaults to in-memory database
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
        self.current_session_id = None
        
    def create_tables(self):
        """Create the necessary database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Create product table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            company TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create inspection sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inspection_sessions (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            batch_number TEXT,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            status TEXT,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        # Create inspection records table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inspection_records (
            id INTEGER PRIMARY KEY,
            session_id INTEGER,
            product_id INTEGER,
            product_name TEXT,
            batch_number TEXT,
            quality TEXT,
            confidence REAL,
            defects TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES inspection_sessions (id)
        )
        ''')
        
        # Create session summaries table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS session_summaries (
            id INTEGER PRIMARY KEY,
            session_id INTEGER,
            timestamp TIMESTAMP,
            product_name TEXT,
            batch_number TEXT,
            company TEXT,
            total_products INTEGER,
            good_products INTEGER,
            defective_products INTEGER,
            duration REAL,
            avg_rate REAL,
            FOREIGN KEY (session_id) REFERENCES inspection_sessions (id)
        )
        ''')
        
        self.conn.commit()
    
    def add_product(self, name, description=None, company=None):
        """
        Add a new product to the database
        
        Args:
            name: Product name
            description: Product description
            company: Company name
            
        Returns:
            ID of the newly created product
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, description, company) VALUES (?, ?, ?)",
            (name, description, company)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_products(self):
        """
        Get all products from the database
        
        Returns:
            DataFrame with all products
        """
        return pd.read_sql("SELECT * FROM products", self.conn)
    
    def start_new_session(self, product_name, batch_number):
        """
        Start a new inspection session
        
        Args:
            product_name: Name of the product being inspected
            batch_number: Batch number for the inspection
            
        Returns:
            ID of the newly created session
        """
        # Get or create product ID
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM products WHERE name = ?", (product_name,))
        result = cursor.fetchone()
        
        if result:
            product_id = result[0]
        else:
            product_id = self.add_product(product_name)
        
        # Create new session
        cursor.execute(
            "INSERT INTO inspection_sessions (product_id, batch_number, start_time, status) VALUES (?, ?, ?, ?)",
            (product_id, batch_number, datetime.now(), "active")
        )
        self.conn.commit()
        
        self.current_session_id = cursor.lastrowid
        return self.current_session_id
    
    def end_session(self, session_id=None):
        """
        End an inspection session
        
        Args:
            session_id: ID of the session to end, defaults to current session
        """
        if session_id is None:
            session_id = self.current_session_id
            
        if session_id:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE inspection_sessions SET end_time = ?, status = ? WHERE id = ?",
                (datetime.now(), "completed", session_id)
            )
            self.conn.commit()
    
    def add_inspection_record(self, product_id, product_name, batch_number, quality, confidence, defects=None, timestamp=None):
        """
        Add a new inspection record
        
        Args:
            product_id: ID of the inspected product
            product_name: Name of the product
            batch_number: Batch number
            quality: Quality assessment result ('good' or 'bad')
            confidence: Confidence score of the assessment
            defects: List of detected defects (optional)
            timestamp: Timestamp of the inspection (defaults to now)
            
        Returns:
            ID of the newly created record
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        if defects is not None and not isinstance(defects, str):
            defects = json.dumps(defects)
            
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO inspection_records 
            (session_id, product_id, product_name, batch_number, quality, confidence, defects, timestamp) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (self.current_session_id, product_id, product_name, batch_number, quality, confidence, defects, timestamp)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def add_session_summary(self, summary_data):
        """
        Add a session summary
        
        Args:
            summary_data: Dictionary containing summary information
            
        Returns:
            ID of the newly created summary
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO session_summaries 
            (session_id, timestamp, product_name, batch_number, company, 
             total_products, good_products, defective_products, duration, avg_rate) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.current_session_id,
                summary_data.get('timestamp', datetime.now()),
                summary_data.get('product_name', ''),
                summary_data.get('batch_number', ''),
                summary_data.get('company', ''),
                summary_data.get('total_products', 0),
                summary_data.get('good_products', 0),
                summary_data.get('defective_products', 0),
                summary_data.get('duration', 0),
                summary_data.get('avg_rate', 0)
            )
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_inspection_records(self, session_id=None, limit=None):
        """
        Get inspection records
        
        Args:
            session_id: Filter by session ID (optional)
            limit: Maximum number of records to return (optional)
            
        Returns:
            List of inspection records
        """
        query = "SELECT * FROM inspection_records"
        params = []
        
        if session_id:
            query += " WHERE session_id = ?"
            params.append(session_id)
            
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
            
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_inspection_records_df(self, session_id=None, limit=None):
        """
        Get inspection records as a DataFrame
        
        Args:
            session_id: Filter by session ID (optional)
            limit: Maximum number of records to return (optional)
            
        Returns:
            DataFrame with inspection records
        """
        query = "SELECT * FROM inspection_records"
        params = []
        
        if session_id:
            query += " WHERE session_id = ?"
            params.append(session_id)
            
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
            
        return pd.read_sql(query, self.conn, params=params)
    
    def get_session_summaries(self, limit=None):
        """
        Get session summaries
        
        Args:
            limit: Maximum number of summaries to return (optional)
            
        Returns:
            DataFrame with session summaries
        """
        query = "SELECT * FROM session_summaries ORDER BY timestamp DESC"
        
        if limit:
            query += f" LIMIT {limit}"
            
        return pd.read_sql(query, self.conn)
    
    def get_statistics(self):
        """
        Get overall statistics
        
        Returns:
            Dictionary with statistics
        """
        # Get total counts
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM inspection_records")
        total_inspections = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM inspection_records WHERE quality = 'good'")
        good_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM inspection_records WHERE quality = 'bad'")
        bad_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT session_id) FROM inspection_records")
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT product_name) FROM inspection_records")
        total_products = cursor.fetchone()[0]
        
        # Calculate percentages
        good_percentage = (good_count / total_inspections * 100) if total_inspections > 0 else 0
        bad_percentage = (bad_count / total_inspections * 100) if total_inspections > 0 else 0
        
        return {
            'total_inspections': total_inspections,
            'good_count': good_count,
            'bad_count': bad_count,
            'good_percentage': good_percentage,
            'bad_percentage': bad_percentage,
            'total_sessions': total_sessions,
            'total_products': total_products
        }
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            
    def __del__(self):
        """Cleanup on object destruction"""
        self.close()
