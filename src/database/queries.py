from .connection import DatabaseConnection
import pandas as pd

class EmployeeQueries:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def get_employee_count(self):
        """Get total number of employees"""
        query = "SELECT COUNT(*) as total_employees FROM employees"
        return self.db.execute_query(query)
    
    def get_department_summary(self):
        """Get employee count by department"""
        query = """
        SELECT d.dept_name, COUNT(de.emp_no) as employee_count
        FROM departments d
        LEFT JOIN dept_emp de ON d.dept_no = de.dept_no
        WHERE de.to_date = '9999-01-01'
        GROUP BY d.dept_name
        ORDER BY employee_count DESC
        """
        return self.db.execute_query(query)
    
    def get_salary_statistics(self):
        """Get salary statistics"""
        query = """
        SELECT 
            AVG(salary) as avg_salary,
            MIN(salary) as min_salary,
            MAX(salary) as max_salary,
            COUNT(*) as total_records
        FROM salaries 
        WHERE to_date = '9999-01-01'
        """
        return self.db.execute_query(query)
    
    def get_employees_by_hire_year(self, year):
        """Get employees hired in a specific year"""
        query = """
        SELECT first_name, last_name, hire_date, gender
        FROM employees 
        WHERE YEAR(hire_date) = %s
        ORDER BY hire_date
        """
        return self.db.execute_query(query, (year,))
    
    def execute_custom_query(self, sql_query):
        """Execute a custom SQL query"""
        return self.db.execute_query(sql_query)
