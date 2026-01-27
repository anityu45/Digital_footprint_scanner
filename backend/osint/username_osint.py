import subprocess
import sys
import shutil

def check_username_with_sherlock(username):
    """
    Runs the OFFICIAL Sherlock tool to find accounts.
    """
    print(f"🕵️ Starting Deep Sherlock Scan for: {username}...")
    
    # Check if sherlock is installed
    sherlock_cmd = shutil.which("sherlock")
    if not sherlock_cmd:
        # Fallback if installed via pip as a module
        command = [sys.executable, "-m", "sherlock", username, "--timeout", "1", "--print-found"]
    else:
        command = [sherlock_cmd, username, "--timeout", "1", "--print-found"]

    try:
        # Run the process
        result = subprocess.run(command, capture_output=True, text=True)
        findings = []
        
        # Parse output
        for line in result.stdout.splitlines():
            if "[+]" in line:
                # Format: "[+] SiteName: URL"
                clean = line.replace("[+]", "").strip()
                if ": " in clean:
                    parts = clean.split(": ", 1)
                    findings.append({"site": parts[0], "url": parts[1]})
        
        return findings

    except Exception as e:
        print(f"Sherlock Error: {e}")
        return []

# Wrapper
def check_username_list(username):
    return check_username_with_sherlock(username)