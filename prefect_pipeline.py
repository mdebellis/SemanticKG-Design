import prefect
from prefect import task, flow
import os
import shutil
from src.read_csv import read_csv, conn
import glob

# Define the source and destination directories
source_dir = 'data/data_for_pipeline'
dest_dir = 'data/processed_data'

@task
def process_csv_file(file_path):
    """
    Task to process a single CSV file and move it to the destination directory.
    """
    logger = prefect.get_run_logger()
    try:
        logger.info(f"Processing file: {file_path}")
        read_csv(file_path)
        
        # Move the processed file to the destination directory
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(dest_dir, file_name)
        shutil.move(file_path, dest_path)
        logger.info(f"Moved file {file_path} to {dest_path}")
    except Exception as e:
        logger.error(f"Failed to process file {file_path}: {e}")
        raise

@flow(name="CSV Processing Pipeline")
def csv_processing_pipeline():
    """
    A Prefect pipeline to process CSV files from a source directory
    and move them to a destination directory.
    """
    logger = prefect.get_run_logger()
    
    # Ensure the destination directory exists
    os.makedirs(dest_dir, exist_ok=True)

    # Find all CSV files in the source directory
    csv_files = glob.glob(os.path.join(source_dir, '*.csv'))
    
    if not csv_files:
        logger.info("No CSV files found to process.")
        return

    logger.info(f"Found {len(csv_files)} CSV files to process.")
    
    for csv_file in csv_files:
        process_csv_file.submit(csv_file)

if __name__ == "__main__":
    csv_processing_pipeline()
    # Close the AllegroGraph connection
    conn.close() 