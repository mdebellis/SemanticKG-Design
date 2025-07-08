"""
Semantic Knowledge Graph Data Pipeline

This pipeline runs daily at 9am PST to:
1. Check for new CSV files in data/data_for_pipeline/
2. Process each file using the load_csv function
3. Move processed files to data/processed_data/
"""

import os
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List

from prefect import flow, task

# Import our custom CSV processing function
from src.test_read_csv import load_csv

# Configuration
INPUT_DIR = "data/data_for_pipeline"
PROCESSED_DIR = "data/processed_data"
DEFAULT_CLASS_IRI = "https://www.michaeldebellis.com/climate_obstruction/Report"

# Pacific Time zone for scheduling
PST = timezone(timedelta(hours=-8))
PDT = timezone(timedelta(hours=-7))


@task(name="scan_for_csv_files")
def scan_for_csv_files(directory: str) -> List[str]:
    """
    Scan the input directory for CSV files.
    
    Args:
        directory: Directory path to scan
        
    Returns:
        List of CSV file paths found
    """
    csv_files = []
    input_path = Path(directory)
    
    if not input_path.exists():
        print(f"Input directory {directory} does not exist")
        return csv_files
    
    for file_path in input_path.glob("*.csv"):
        if file_path.is_file():
            csv_files.append(str(file_path))
            print(f"Found CSV file: {file_path}")
    
    print(f"Total CSV files found: {len(csv_files)}")
    return csv_files


@task(name="process_csv_file")
def process_csv_file(file_path: str, class_iri: str = DEFAULT_CLASS_IRI) -> dict:
    """
    Process a single CSV file using the load_csv function.
    
    Args:
        file_path: Path to the CSV file to process
        class_iri: IRI string for the class to create instances from
        
    Returns:
        Dictionary with processing results
    """
    try:
        print(f"Processing file: {file_path}")
        
        # Call the load_csv function from test_read_csv.py
        lines_processed = load_csv(file_path, class_iri)
        
        result = {
            "file_path": file_path,
            "status": "success",
            "lines_processed": lines_processed,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"Successfully processed {lines_processed} lines from {file_path}")
        return result
        
    except Exception as e:
        error_result = {
            "file_path": file_path,
            "status": "error",
            "error_message": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"Error processing {file_path}: {e}")
        return error_result


@task(name="move_processed_file")
def move_processed_file(file_path: str, processed_dir: str) -> bool:
    """
    Move a processed file to the processed directory.
    
    Args:
        file_path: Path to the file to move
        processed_dir: Directory to move the file to
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure processed directory exists
        Path(processed_dir).mkdir(parents=True, exist_ok=True)
        
        source_path = Path(file_path)
        # Add timestamp to filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_parts = source_path.stem, timestamp, source_path.suffix
        new_filename = f"{filename_parts[0]}_{filename_parts[1]}{filename_parts[2]}"
        
        destination_path = Path(processed_dir) / new_filename
        
        # Move the file
        shutil.move(str(source_path), str(destination_path))
        print(f"Moved {file_path} to {destination_path}")
        
        return True
        
    except Exception as e:
        print(f"Error moving file {file_path}: {e}")
        return False


@flow(name="semantic-kg-data-pipeline")
def data_pipeline_flow():
    """
    Main pipeline flow that orchestrates the entire data processing workflow.
    """
    print("Starting Semantic KG Data Pipeline...")
    print(f"Checking for CSV files in: {INPUT_DIR}")
    
    # Step 1: Scan for CSV files
    csv_files = scan_for_csv_files(INPUT_DIR)
    
    if not csv_files:
        print("No CSV files found. Pipeline completed.")
        return {"status": "completed", "files_processed": 0}
    
    # Step 2: Process each CSV file
    results = []
    successful_files = []
    
    for csv_file in csv_files:
        # Process the file
        result = process_csv_file(csv_file)
        results.append(result)
        
        # If processing was successful, mark for moving
        if result["status"] == "success":
            successful_files.append(csv_file)
    
    # Step 3: Move successfully processed files
    moved_files = []
    for file_path in successful_files:
        if move_processed_file(file_path, PROCESSED_DIR):
            moved_files.append(file_path)
    
    # Summary
    summary = {
        "status": "completed",
        "files_found": len(csv_files),
        "files_processed_successfully": len(successful_files),
        "files_moved": len(moved_files),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"Pipeline completed. Processed {len(successful_files)} files successfully.")
    return summary


# For Prefect 3.x deployment using the new serve() method
def serve_pipeline():
    """Serve the pipeline with scheduling (Prefect 3.x approach)."""
    # In Prefect 3.x, use flow.serve() for deployment
    data_pipeline_flow.serve(
        name="semantic-kg-pipeline-daily",
        cron="0 17 * * *",  # 17:00 UTC = 9:00 AM PST
        description="Daily data pipeline for Semantic Knowledge Graph processing",
        tags=["semantic-kg", "csv-processing", "daily"]
    )


if __name__ == "__main__":
    # For testing - run the pipeline immediately
    print("Running pipeline manually for testing...")
    result = data_pipeline_flow()
    print("Pipeline result:", result) 