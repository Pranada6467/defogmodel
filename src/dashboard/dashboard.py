import gradio as gr
import pandas as pd
from src.database.queries import EmployeeQueries
from src.llm.sql_generator import SQLGenerator
import logging

logger = logging.getLogger(__name__)

class EmployeeDashboard:
    def __init__(self):
        self.queries = EmployeeQueries()
        self.sql_generator = SQLGenerator()
        self.sql_generator.load_model()
    
    def get_basic_stats(self):
        """Get basic employee statistics"""
        try:
            emp_count = self.queries.get_employee_count()
            dept_summary = self.queries.get_department_summary()
            salary_stats = self.queries.get_salary_statistics()
            
            return emp_count, dept_summary, salary_stats
        except Exception as e:
            logger.error(f"Error getting basic stats: {e}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    def process_natural_language_query(self, question):
        """Process natural language question and return SQL + results"""
        try:
            # Generate SQL from question
            sql_query = self.sql_generator.generate_sql(question)
            
            # Validate SQL
            is_valid, validation_msg = self.sql_generator.validate_sql(sql_query)
            
            if not is_valid:
                return f"Invalid SQL: {validation_msg}", pd.DataFrame(), sql_query
            
            # Execute query
            results = self.queries.execute_custom_query(sql_query)
            
            return "Query executed successfully", results, sql_query
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            logger.error(error_msg)
            return error_msg, pd.DataFrame(), ""
    
    def execute_custom_sql(self, sql_query):
        """Execute custom SQL query"""
        try:
            # Validate SQL
            is_valid, validation_msg = self.sql_generator.validate_sql(sql_query)
            
            if not is_valid:
                return f"Invalid SQL: {validation_msg}", pd.DataFrame()
            
            results = self.queries.execute_custom_query(sql_query)
            return "Query executed successfully", results
            
        except Exception as e:
            error_msg = f"Error executing query: {str(e)}"
            logger.error(error_msg)
            return error_msg, pd.DataFrame()
    
    def create_dashboard(self):
        """Create the Gradio dashboard"""
        with gr.Blocks(title="Employee Analytics Dashboard", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 📊 Employee Analytics Dashboard")
            gr.Markdown("Analyze employee data using natural language queries powered by AI")
            
            with gr.Tabs():
                # Overview Tab
                with gr.TabItem("📈 Overview"):
                    gr.Markdown("## Database Overview")
                    
                    with gr.Row():
                        with gr.Column():
                            emp_count_df = gr.DataFrame(label="Total Employees")
                            salary_stats_df = gr.DataFrame(label="Salary Statistics")
                        
                        with gr.Column():
                            dept_summary_df = gr.DataFrame(label="Department Summary")
                    
                    refresh_btn = gr.Button("🔄 Refresh Data", variant="primary")
                    
                    def refresh_data():
                        emp_count, dept_summary, salary_stats = self.get_basic_stats()
                        return emp_count, salary_stats, dept_summary
                    
                    refresh_btn.click(
                        refresh_data,
                        outputs=[emp_count_df, salary_stats_df, dept_summary_df]
                    )
                    
                    # Load initial data
                    demo.load(refresh_data, outputs=[emp_count_df, salary_stats_df, dept_summary_df])
                
                # Natural Language Query Tab
                with gr.TabItem("🤖 AI Query Generator"):
                    gr.Markdown("## Ask Questions in Natural Language")
                    gr.Markdown("Examples: 'How many employees are there?', 'Show me the highest paid employees', 'What are the different departments?'")
                    
                    question_input = gr.Textbox(
                        label="Your Question",
                        placeholder="Ask anything about the employee database...",
                        lines=2
                    )
                    
                    with gr.Row():
                        generate_btn = gr.Button("🔮 Generate & Execute Query", variant="primary")
                        clear_btn = gr.Button("🗑️ Clear", variant="secondary")
                    
                    status_output = gr.Textbox(label="Status", interactive=False)
                    generated_sql = gr.Code(label="Generated SQL Query", language="sql")
                    query_results = gr.DataFrame(label="Query Results")
                    
                    generate_btn.click(
                        self.process_natural_language_query,
                        inputs=[question_input],
                        outputs=[status_output, query_results, generated_sql]
                    )
                    
                    clear_btn.click(
                        lambda: ("", "", pd.DataFrame(), ""),
                        outputs=[question_input, status_output, query_results, generated_sql]
                    )
                
                # Custom SQL Tab
                with gr.TabItem("⚡ Custom SQL"):
                    gr.Markdown("## Execute Custom SQL Queries")
                    gr.Markdown("⚠️ **Note**: Only SELECT queries are allowed for security reasons")
                    
                    sql_input = gr.Code(
                        label="SQL Query",
                        language="sql",
                        placeholder="SELECT * FROM employees LIMIT 10;",
                        lines=5
                    )
                    
                    with gr.Row():
                        execute_btn = gr.Button("▶️ Execute Query", variant="primary")
                        clear_sql_btn = gr.Button("🗑️ Clear", variant="secondary")
                    
                    sql_status = gr.Textbox(label="Status", interactive=False)
                    sql_results = gr.DataFrame(label="Query Results")
                    
                    execute_btn.click(
                        self.execute_custom_sql,
                        inputs=[sql_input],
                        outputs=[sql_status, sql_results]
                    )
                    
                    clear_sql_btn.click(
                        lambda: ("", "", pd.DataFrame()),
                        outputs=[sql_input, sql_status, sql_results]
                    )
        
        return demo

def create_app():
    """Create and return the Gradio app"""
    dashboard = EmployeeDashboard()
    return dashboard.create_dashboard()
