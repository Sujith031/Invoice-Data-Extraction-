# src/invoice_data_extraction/logging/__init__.py

import logging

def setup_logging():
    """Configures the logging settings."""
    logging.basicConfig(
        level=logging.DEBUG,  # Adjust logging level as needed
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log"),  # Log to a file
            logging.StreamHandler()            # Log to console
        ]
    )
