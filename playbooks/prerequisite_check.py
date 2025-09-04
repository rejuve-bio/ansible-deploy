#!/usr/bin/env python3
import shutil
import subprocess
import sys
import os
import grp
import os
import subprocess

def install_uv():
    """Install UV into the current user's ~/.local/bin"""
    home_dir = os.path.expanduser("~")   
    uv_install_path = os.path.join(home_dir, ".local", "bin")

    # Ensure the bin directory exists
    os.makedirs(uv_install_path, exist_ok=True)

    print(f"📥 Installing UV to {uv_install_path} ...")
    try:
        # Run the installer in the user's bin directory
        result = subprocess.run(
            f"curl -LsSf https://astral.sh/uv/install.sh | sh",
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ, "UV_PREFIX": uv_install_path}  
        )

        if result.returncode == 0:
            print("✅ UV installed successfully.")

            # Add the bin directory to PATH for this Python session
            if uv_install_path not in os.environ['PATH']:
                os.environ['PATH'] = uv_install_path + ":" + os.environ.get('PATH', '')

            # Source ~/.bashrc to make UV available in future shell sessions
            subprocess.run("source ~/.bashrc", shell=True, executable="/bin/bash")

            return True
        else:
            print(f"❌ UV installation failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ UV installation timed out.")
        return False
    except Exception as e:
        print(f"❌ UV installation failed with error: {e}")
        return False

def check_uv():
    """Check if UV is installed, install if missing"""
    if not shutil.which("uv"):
        print("❌ UV is not installed.")
        return install_uv()
    
    # Check UV version
    try:
        result = subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ UV is available ({result.stdout.strip()})")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ UV is not working properly.")
    return install_uv()

def check_docker_group_exists():
    """Check if docker group exists on the system"""
    try:
        grp.getgrnam('docker')
        return True
    except KeyError:
        return False

def create_docker_group():
    """Create docker group if it doesn't exist"""
    print("📦 Creating docker group...")
    try:
        result = subprocess.run(
            ["groupadd", "docker"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ Docker group created successfully.")
            return True
        else:
            # Group might already exist
            if "group exists" in result.stderr.lower():
                print("✅ Docker group already exists.")
                return True
            print(f"❌ Failed to create docker group: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Failed to create docker group: {e}")
        return False

def check_docker():
    """Check if Docker is installed and running"""
    # Check if docker command exists
    if not shutil.which("docker"):
        print("❌ Docker is not installed. Please install Docker first.")
        print("   Ubuntu/Debian: sudo apt install docker.io")
        print("   Other systems: https://docs.docker.com/engine/install/")
        return False
    
    # Check if docker group exists, create if not
    if not check_docker_group_exists():
        if not create_docker_group():
            return False
    
    # Check if user is already in docker group
    current_user = os.getenv("USER")
    try:
        docker_group = grp.getgrnam('docker')
        if current_user in docker_group.gr_mem:
            print("✅ User is already in docker group.")
        else:
            print("❌ User not in docker group. Adding to docker group...")
            
            # Add user to docker group
            add_to_group = subprocess.run(
                ["usermod", "-aG", "docker", current_user],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if add_to_group.returncode == 0:
                print("✅ Added user to docker group successfully.")
                print("💡 Please log out and back in for changes to take effect, or run: newgrp docker")
                # Continue anyway since Docker might work with sudo
            else:
                print(f"❌ Failed to add user to docker group: {add_to_group.stderr}")
                # Continue anyway since Docker might work with sudo
    except KeyError:
        print("❌ Docker group doesn't exist (this shouldn't happen after creation)")
        return False
    
    # Check if Docker daemon is running
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print("❌ Docker is installed but not running.")
            print("   Start Docker with: sudo systemctl start docker")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Docker is not responding. Please ensure Docker is installed and running.")
        return False
    
    print("✅ Docker is installed and running properly.")
    return True

def check_docker_compose():
    """Check if Docker Compose is available"""
    # First try with sudo (in case user isn't in docker group yet)
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ Docker Compose is available (with sudo).")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Try without sudo (if user is in docker group)
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ Docker Compose is available.")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Fallback to docker-compose command with sudo
    try:
        result = subprocess.run(
            ["sudo","docker-compose", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ Docker Compose (standalone) is available (with sudo).")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Fallback to docker-compose command without sudo
    if shutil.which("docker-compose"):
        print("✅ Docker Compose (standalone) is available.")
        return True
    
    print("❌ Docker Compose is not installed.")
    print("   Install with: sudo apt install docker-compose")
    print("   Or use Docker Compose Plugin: https://docs.docker.com/compose/install/")
    return False

def main():
    print("🔍 Checking prerequisites...")
    print("=" * 50)
    
    uv_ok = check_uv()
    print()
    
    docker_ok = check_docker()
    print()
    
    compose_ok = check_docker_compose()
    print()
    print("=" * 50)
    
    if not uv_ok or not docker_ok or not compose_ok:
        print("\n💡 Please install the missing prerequisites and try again.")
        sys.exit(1)
    
    print("\n✅ All prerequisites are met! You can proceed with the setup.")
    print("💡 Note: If you were just added to the docker group, you may need to")
    print("   log out and back in for the changes to take full effect.")
    sys.exit(0)

if __name__ == "__main__":
    main()