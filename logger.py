import logging as lg
import os
from datetime import datetime

def initialise_logger():
    # Create a logs directory
    logs_path = './logs'
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)

    # Generate a unique log file name with the current date and time
    log_name = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    log_file = os.path.join(logs_path, log_name)

    # Basic logger configuration
    lg.basicConfig(
        filename=log_file,
        format='%(asctime)s - %(levelname)s: %(message)s',
        level=lg.DEBUG
    )

    # Add a console handler for real-time logging
    console_handler = lg.StreamHandler()
    console_handler.setLevel(lg.DEBUG)
    console_handler.setFormatter(lg.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
    lg.getLogger().addHandler(console_handler)

    lg.info("Logger initialized successfully.")
    print(f"Log file created at: {log_file}")
