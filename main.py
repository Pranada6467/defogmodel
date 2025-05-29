#!/usr/bin/env python3
"""
Employee Analytics Dashboard
Main application entry point
"""

import logging
import sys
import os
from src.dashboard.app import create_app

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main application function"""
    try:
        logger.info("Starting Employee Analytics Dashboard...")
        
        # Create and launch the Gradio app
        app = create_app()
        
        # Launch with appropriate settings
        app.launch(
            server_name="0.0.0.0",  # Allow external access
            server_port=7860,
            share=False,  # Set to True if you want a public link
            debug=False
        )
        
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
