import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import sqlparse
from config.database import EMPLOYEES_SCHEMA
import logging

logger = logging.getLogger(__name__)

class SQLGenerator:
    def __init__(self, model_name="defog/sqlcoder-34b-alpha"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
    
    def load_model(self):
        """Load the SQLCoder model"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Load model with appropriate settings based on available hardware
            if self.device == "cuda":
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    trust_remote_code=True,
                    torch_dtype=torch.float16,
                    load_in_4bit=True,
                    device_map="auto",
                    use_cache=True,
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    trust_remote_code=True,
                    device_map="cpu",
                    use_cache=True,
                )
            
            logger.info("Model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def generate_sql(self, question):
        """Generate SQL query from natural language question"""
        if not self.model or not self.tokenizer:
            if not self.load_model():
                return "Error: Could not load model"
        
        prompt = f"""Task: Generate a MySQL query to answer the following question.

Database Schema:
{EMPLOYEES_SCHEMA}

Question: {question}

Instructions:
- Generate only valid MySQL syntax
- Use proper table joins when needed
- Include appropriate WHERE clauses for filtering
- If the question cannot be answered with the available schema, return 'I do not know'

SQL Query:
"""
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt")
            if self.device == "cuda":
                inputs = inputs.to("cuda")
            
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    num_return_sequences=1,
                    eos_token_id=self.tokenizer.eos_token_id,
                    pad_token_id=self.tokenizer.eos_token_id,
                    max_new_tokens=500,
                    do_sample=False,
                    num_beams=1,
                    temperature=0.1
                )
            
            outputs = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
            
            # Extract SQL from the output
            sql_output = outputs[0].split("SQL Query:")[-1].strip()
            
            # Clean and format the SQL
            formatted_sql = sqlparse.format(sql_output, reindent=True, keyword_case='upper')
            
            return formatted_sql
            
        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            return f"Error generating query: {str(e)}"
    
    def validate_sql(self, sql_query):
        """Basic SQL validation"""
        try:
            parsed = sqlparse.parse(sql_query)
            if not parsed:
                return False, "Invalid SQL syntax"
            
            # Check for dangerous operations
            dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
            sql_upper = sql_query.upper()
            
            for keyword in dangerous_keywords:
                if keyword in sql_upper:
                    return False, f"Dangerous operation detected: {keyword}"
            
            return True, "Valid SQL"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
