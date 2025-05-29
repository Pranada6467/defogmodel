import mysql.connector
from mysql.connector import Error
import pandas as pd
from config.database import DATABASE_CONFIG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(**DATABASE_CONFIG)
            self.cursor = self.connection.cursor()
            logger.info("Successfully connected to MySQL database")
            return True
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a SELECT query and return results as DataFrame"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            df = pd.read_sql(query, self.connection, params=params)
            return df
        except Error as e:
            logger.error(f"Error executing query: {e}")
            return pd.DataFrame()
    
    def execute_raw_query(self, query, params=None):
        """Execute raw query and return cursor results"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Error as e:
            logger.error(f"Error executing raw query: {e}")
            return []
    
    def get_table_info(self):
        """Get information about all tables in the database"""
        query = "SHOW TABLES"
        tables = self.execute_raw_query(query)
        
        table_info = {}
        for table in tables:
            table_name = table[0]
            desc_query = f"DESCRIBE {table_name}"
            columns = self.execute_raw_query(desc_query)
            table_info[table_name] = columns
        
        return table_info
