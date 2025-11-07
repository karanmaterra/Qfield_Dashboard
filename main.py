import subprocess
import sys
import os
from datetime import datetime

def run_git_commands():
    """Run git add, commit, and push before Script A."""
    repo_dir = r"C:\Users\karan.daphade_materr\Desktop\streamlit-dashboard"

    print("Using Git Repo:", repo_dir)

    # ✅ Verify that .git folder exists
    git_folder = os.path.join(repo_dir, ".git")
    if not os.path.exists(git_folder):
        print(f"✗ ERROR: .git folder NOT found at {repo_dir}")
        return False

    print("Running Git Commands...")

    try:
        # git add .
        subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)

        # git commit -m "<timestamp>"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"Auto update on {timestamp}"

        # Avoid failure when no changes exist
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=repo_dir,
            check=False  # ✅ no error if commit is empty
        )

        # git push
        subprocess.run(["git", "push"], cwd=repo_dir, check=True)

        print("✓ Git push completed successfully")
        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Git command failed: {e}")
        return False




def run_script_a():
    """Run script A to merge all CSV files"""
    script_a_path = r"C:\Users\karan.daphade_materr\Desktop\July\CSV\fastdownload\downloadmerge.py"
    
    if not os.path.exists(script_a_path):
        print(f"Error: Script A not found at {script_a_path}")
        return False
    
    print("Running Script A (merging CSV files)...")
    try:
        result = subprocess.run(
            [sys.executable, script_a_path],
            check=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(script_a_path)
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
    
    if not os.path.exists(script_b_path):
        print(f"Error: Script B not found at {script_b_path}")
        return False
    
    print("Running Script B (launching dashboard)...")
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "dashboard.py"],
            cwd=script_b_dir
        )
        process.wait()
        return True
    except subprocess.CalledProcessError as e:
        print(f"Script B ended with error: {e}")
        return False
    except KeyboardInterrupt:
        print("\nDashboard closed by user")
        return True



def main():
    print("=" * 60)
    print("Starting: Git Push → CSV Merge → Dashboard")
    print("=" * 60)

    # ✅ FIRST RUN GIT COMMANDS
    if not run_git_commands():
        print("Stopping process due to Git failure.")
        return

    # ✅ THEN RUN SCRIPT A
    success = run_script_a()

    if not success:
        print("Failed to run Script A. Exiting.")
        return
    
    # ✅ THEN RUN SCRIPT B
    print("\n" + "=" * 60)
    print("Launching Dashboard with Updated Data")
    print("=" * 60)
    run_script_b()



if __name__ == "__main__":
    main()
