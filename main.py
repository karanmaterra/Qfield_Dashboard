import subprocess
import sys
import os
from pathlib import Path

def run_script_a():
    """Run script A to merge all CSV files"""
    script_a_path = r"C:\Users\karan.daphade_materr\Desktop\July\CSV\fastdownload\downloadmerge.py"
    
    # Check if script A exists
    if not os.path.exists(script_a_path):
        print(f"Error: Script A not found at {script_a_path}")
        return False
    
    print("Running Script A (merging CSV files)...")
    try:
        # Run script A
        result = subprocess.run(
            [sys.executable, script_a_path],
            check=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(script_a_path)  # Run in script's directory
        )
        print("✓ Script A completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Script A failed with error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def run_script_b():
    """Run script B to launch the Streamlit dashboard"""
    script_b_dir = r"C:\Users\karan.daphade_materr\Desktop\streamlit-dashboard"
    script_b_path = os.path.join(script_b_dir, "dashboard.py")
    
    # Check if script B exists
    if not os.path.exists(script_b_path):
        print(f"Error: Script B not found at {script_b_path}")
        return False
    
    print("Running Script B (launching dashboard)...")
    try:
        # Run script B using streamlit
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "dashboard.py"],
            cwd=script_b_dir  # Run in script's directory
        )
        # Wait for the process to complete
        process.wait()
        return True
    except subprocess.CalledProcessError as e:
        print(f"Script B ended with error: {e}")
        return False
    except KeyboardInterrupt:
        print("\nDashboard closed by user")
        return True

def main():
    """Main function to run both scripts"""
    print("=" * 50)
    print("Starting CSV Merge and Dashboard Process")
    print("=" * 50)
    
    # First run script A to update data
    success = run_script_a()
    
    if not success:
        print("Failed to run Script A. Exiting.")
        return
    
    # Then run script B to show dashboard
    print("\n" + "=" * 50)
    print("Launching Dashboard with Updated Data")
    print("=" * 50)
    run_script_b()

if __name__ == "__main__":
    main()