from pathlib import Path
import subprocess

project_dir = Path(__file__).resolve().parent

# Step 1: Install Python dependencies in isolated venv
subprocess.run(["uv", "sync"], cwd=str(project_dir), check=True)
print("Python dependencies installed in isolated .venv")
