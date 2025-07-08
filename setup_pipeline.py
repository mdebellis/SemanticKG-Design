"""
Setup script for the Semantic Knowledge Graph Data Pipeline

This script helps set up and deploy the Prefect pipeline.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def setup_prefect_pipeline():
    """Set up the Prefect pipeline environment and deployment."""
    
    print("🚀 Setting up Semantic Knowledge Graph Data Pipeline")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("data_pipeline.py").exists():
        print("❌ Error: data_pipeline.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Step 1: Install dependencies
    if not run_command("pip3 install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)
    
    # Step 2: Start Prefect server
    print("\n🌐 Starting Prefect server...")
    print("Note: This will start the Prefect server.")
    print("You can access the UI at http://127.0.0.1:4200")
    
    # In Prefect 3.x, the server start command might be different
    server_start_cmd = "prefect server start"
    print(f"Starting server with: {server_start_cmd}")
    print("Please start the server manually in a separate terminal:")
    print(f"  {server_start_cmd}")
    
    # Step 3: Test the flow
    print("\n🧪 Testing the pipeline flow...")
    if run_command("python3 -c \"from data_pipeline import data_pipeline_flow; print('Flow import successful')\"", "Testing flow import"):
        print("✓ Pipeline flow is ready!")
    else:
        print("⚠️  Warning: Flow import test failed.")
        print("This might be due to missing AllegroGraph dependencies.")
    
    # Step 4: Instructions for deployment
    print("\n📦 Deployment Instructions")
    print("For Prefect 3.x, deployment is simplified:")
    print("1. Start Prefect server: prefect server start")
    print("2. Deploy the flow: python3 -c \"from data_pipeline import serve_pipeline; serve_pipeline()\"")
    print("   OR use: prefect deploy data_pipeline.py:data_pipeline_flow")
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Start Prefect server in a new terminal:")
    print("   prefect server start")
    print("2. Access Prefect UI at: http://127.0.0.1:4200")
    print("3. Test the pipeline manually:")
    print("   python3 data_pipeline.py")
    print("4. For scheduled deployment, run:")
    print("   python3 -c \"from data_pipeline import serve_pipeline; serve_pipeline()\"")
    print("\nPipeline Configuration:")
    print("- Input directory: data/data_for_pipeline/")
    print("- Output directory: data/processed_data/")
    print("- Schedule: Daily at 9:00 AM PST (17:00 UTC)")


if __name__ == "__main__":
    setup_prefect_pipeline() 