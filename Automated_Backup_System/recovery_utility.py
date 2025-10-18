#!/usr/bin/env python3
import subprocess
import os
import sys
import re
import hashlib

# --- Configuration Variables ---
NETWORK_TARGET_DIR = "/home/linux01/Desktop/Automated_Backup_System/network_target_test"
RECOVERY_DIR = "/tmp/restored_files"
TEMP_DIR = "/tmp/recovery_temp"

# --- Utility Functions ---

def run_command(command, error_message):
    """Utility function to run a shell command and check for errors."""
    try:
        # Executes the command and raises an exception on non-zero exit code
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"\nCRITICAL ERROR: {error_message}")
        print(f"Command failed: {e.cmd}")
        print(f"Details: {e.stderr.strip()}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"ERROR: Required utility not found.")
        sys.exit(1)

def list_and_select_backup():
    """Lists available backups and prompts the user for a selection (UX Improvisation)."""
    print("\n--- Available Encrypted Backups ---")
    
    try:
        files = [f for f in os.listdir(NETWORK_TARGET_DIR) if f.endswith('.gpg')]
        if not files:
            print(f"No encrypted backup files found in: {NETWORK_TARGET_DIR}")
            sys.exit(1)
        
        # Sort files by timestamp (latest first)
        files.sort(key=lambda f: re.search(r'backup_(\d{4}-\d{2}-\d{2}_\d{6})', f).group(1), reverse=True)
        backup_map = {}
        
        for i, filename in enumerate(files):
            # Extract timestamp for a user-friendly display
            match = re.search(r'backup_(\d{4}-\d{2}-\d{2}_\d{6})\.tar\.gz\.gpg', filename)
            display_date = match.group(1).replace('_', ' at ') if match else filename
            backup_map[i + 1] = filename
            print(f"  [{i + 1}] -> {display_date} ({'LATEST' if i == 0 else ''})")

        print("---------------------------------")
        
        # Interactive Prompt
        while True:
            try:
                choice = input("Enter the number of the backup to restore (or 'q' to quit): ")
                if choice.lower() == 'q':
                    sys.exit(0)
                choice_index = int(choice)
                if choice_index in backup_map:
                    return backup_map[choice_index]
                else:
                    print("Invalid choice. Please enter a number from the list.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    except Exception as e:
        print(f"ERROR listing backups: {e}")
        sys.exit(1)

def read_and_verify_checksum(decrypted_file, timestamp):
    """Reads the archived checksum and verifies the integrity (Reliability Improvisation)."""
    checksum_filename = f"checksum_{timestamp}.txt"
    
    try:
        # 1. Extract ONLY the checksum file
        run_command(
            f"tar -xf '{decrypted_file}' -C '{TEMP_DIR}' ARCHIVE_ROOT/{checksum_filename}", 
            "Failed to extract internal checksum file."
        )
        
        # 2. Read the expected checksum value
        with open(os.path.join(TEMP_DIR, 'ARCHIVE_ROOT', checksum_filename), 'r') as f:
            expected = f.read().strip()
            
        # 3. Calculate the actual checksum of the data archive
        # We calculate the SHA256 of the data archive file itself, NOT the containing directory.
        data_archive_path = os.path.join(TEMP_DIR, 'ARCHIVE_ROOT', 'data.tar.gz')
        
        # First, extract ONLY the data.tar.gz file (the actual content)
        run_command(
            f"tar -xf '{decrypted_file}' -C '{TEMP_DIR}' ARCHIVE_ROOT/data.tar.gz", 
            "Failed to extract data archive for checksumming."
        )
        
        # Calculate actual checksum of the data file
        hasher = hashlib.sha256()
        with open(data_archive_path, 'rb') as afile:
            buf = afile.read()
            hasher.update(buf)
        actual = hasher.hexdigest()

        # 4. Compare
        if actual == expected:
            print(f"\n✅ INTEGRITY CHECK SUCCESS: Backup file integrity verified.")
            return True
        else:
            print(f"\n❌ INTEGRITY CHECK FAILED: File may be corrupted during transfer or decryption.")
            print(f"   Expected Checksum: {expected}")
            print(f"   Actual Checksum: {actual}")
            return False

    except Exception as e:
        print(f"Error during checksum verification: {e}")
        return False

def cleanup():
    """Removes the entire temporary recovery directory."""
    if os.path.exists(TEMP_DIR):
        print(f"Cleaning up temporary directory: {TEMP_DIR}")
        subprocess.run(f"rm -rf '{TEMP_DIR}'", shell=True)

# --- Main Recovery Process ---

def restore_files():
    # Perform cleanup initially in case of previous failure
    cleanup()
    
    try:
        # 1. Interactive Selection
        backup_file = list_and_select_backup()
        
        # Extract timestamp for checksum verification
        match = re.search(r'backup_(\d{4}-\d{2}-\d{2}_\d{6})', backup_file)
        if not match:
            print("ERROR: Could not parse timestamp from backup filename.")
            sys.exit(1)
            
        timestamp = match.group(1)
        
        source_path = os.path.join(NETWORK_TARGET_DIR, backup_file)
        local_encrypted_file = os.path.join(TEMP_DIR, backup_file)
        decrypted_file = os.path.join(TEMP_DIR, backup_file.replace(".gpg", "")) # Path to the final decrypted tar.gz

        os.makedirs(TEMP_DIR, exist_ok=True)
        
        # 2. Securely Retrieve the Encrypted File (rsync)
        print(f"\nRetrieving encrypted file: {backup_file}...")
        rsync_command = f"rsync -avz '{source_path}' {TEMP_DIR}/"
        run_command(rsync_command, "File retrieval failed.")

        # 3. Decrypt the Archive (GPG Key Pair)
        print(f"Decrypting file using private key. Please enter your GPG Private Key Passphrase...")
        # GPG automatically prompts for the private key passphrase
        gpg_command = f"gpg --batch --yes --output '{decrypted_file}' --decrypt '{local_encrypted_file}'"
        run_command(gpg_command, "Decryption failed. Ensure your private key is available and the passphrase is correct.")

        # 4. Integrity Check (SHA256)
        if not read_and_verify_checksum(decrypted_file, timestamp):
            print("Restoration Halted due to failed integrity check.")
            sys.exit(1)
            
        # 5. Extract the Archive (tar)
        print(f"Creating recovery directory: {RECOVERY_DIR}")
        os.makedirs(RECOVERY_DIR, exist_ok=True)
        print(f"Extracting archive contents to: {RECOVERY_DIR}")
        
        # Extract the final 'data.tar.gz' file from the ARCHIVE_ROOT folder
        tar_command = f"tar -xf '{decrypted_file}' -C '{TEMP_DIR}' ARCHIVE_ROOT/data.tar.gz"
        run_command(tar_command, "Failed to extract final data archive.")

        # Extract the contents of data.tar.gz to the recovery directory
        final_extract_command = f"tar -xzf '{os.path.join(TEMP_DIR, 'ARCHIVE_ROOT', 'data.tar.gz')}' -C '{RECOVERY_DIR}'"
        run_command(final_extract_command, "Failed to extract final data contents.")


        print(f"\nSUCCESS! Files restored to: {RECOVERY_DIR}/home/linux01/Desktop/Automated_Backup_System/source_data")
        # NOTE: The path is verbose because tar retains the full path when extracted from data.tar.gz

    finally:
        # 6. Final Clean Up
        cleanup()


if __name__ == "__main__":
    restore_files()
