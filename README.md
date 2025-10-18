🛡️ Automated  3-2-1 Data Backup & Recovery System

This project engineers a robust, self-auditing data backup solution for Linux environments, automating compression, asymmetric encryption (GPG Key Pair), and scheduled transfer to ensure data survivability according to the 3-2-1 backup rule.

It demonstrates mastery of system automation, security protocols, and data integrity verification.

📁 Project Setup

To ensure all absolute paths in the scripts work correctly, create a dedicated project folder inside your user's home directory (~).

Create the Main Project Directory:

mkdir -p ~/Desktop/Automated_Backup_System
cd ~/Desktop/Automated_Backup_System


File Placement:

Place backup_core.sh and recovery_utility.py directly inside the Automated_Backup_System folder.

Create the source_data and network_target_test folders as outlined in the configuration steps.

Add your file into source_data folder (eg: test_file.txt).

✨ Key Features & Security Protocols

Focus Area

Feature Implemented

Security/Reliability

3-2-1 Compliance

Triple Copy Transfer

Data is secured on a Local Drive (Copy 1), a Network Target (Copy 2 - rsync), and an Offsite Cloud (Copy 3 - rclone).

Encryption

GPG Key Pair Encryption

Replaces hardcoded passwords with asymmetric keys. Encryption uses the Public Key, and decryption requires the Private Key Passphrase.

Integrity

SHA256 Verification

Calculates a checksum before encryption and verifies it after decryption. This prevents corrupted files from being restored due to network errors.

Robustness

Automated Auditing

Includes detailed logging and sends Email Alerts upon success or critical failure (mailutils).

User Experience

Interactive Recovery

The recovery utility lists all available backup versions, allowing the user to select a specific date/time to restore.

🛠️ Prerequisites

Before running the system, ensure the following utilities are installed in your Linux environment (Kali/Ubuntu/Debian):

GPG (GnuPG): For asymmetric encryption. (Usually pre-installed)

rsync: For fast, network-efficient local transfers. (Usually pre-installed)

rclone: For secure offsite cloud transfer (Step 7).

mailutils: For email alerting on success/failure.

# Install rclone and mail utilities
sudo -v ; curl [https://rclone.org/install.sh](https://rclone.org/install.sh) | sudo bash
sudo apt update && sudo apt install mailutils




⚙️ Configuration (One-Time Setup)

1. Generate and Register Your GPG Key

This step creates the key pair needed for encryption/decryption:

Action

Command

Note

Generate Keys

gpg --full-generate-key

Choose RSA 4096 bits. Create a strong Private Key Passphrase.

Find Key ID

gpg --list-keys

Locate the 8- or 16-character ID. This is your RECIPIENT_ID.

2. Configure the Cloud Remote (rclone)

Run the following command and follow the prompts (select your cloud provider, often Google Drive). Crucially, note the name you give the remote.

rclone config




3. Update Script Variables

Edit the backup_core.sh script and replace the placeholder values in the Configuration Variables section with your actual details:

Variable

Placeholder

Your Value

Note

RECIPIENT_ID

[YOUR_GPG_KEY_ID]

Paste the key ID from the step above.

Required for Encryption.

ALERT_EMAIL

linux01@localhost

Change to your actual email address.

Required for Email Alerts.

CLOUD_REMOTE

[YOUR_CORRECT_REMOTE_NAME]:Encrypted_Backups

Use the exact name you saved in rclone config (e.g., my_gdrive:Encrypted_Backups).

Required for Offsite Copy.

✅ Verification & Auditing

After running the backup or recovery scripts, use these locations and commands to confirm the steps completed successfully and audit the system's status.

A. Checking the Backup Process (backup_core.sh)

Step

Location

Command / Action

Verification Result

Logging

/tmp/

ls -l /tmp/backup_log_*.txt

Audit: A new log file should exist, confirming all steps ran.

Copy 2 (Network)

./network_target_test/

ls -l network_target_test/*.gpg

Transfer Success: A large, encrypted .gpg file should be present.

Copy 3 (Offsite)

Your Cloud Provider

Manually check your cloud folder (Encrypted_Backups)

Offsite Success: The encrypted .gpg file should be uploaded to the cloud (Google Drive/Dropbox).

Alerts

Your Mailbox

Check the mailbox for the configured ALERT_EMAIL.

Robustness: A "SUCCESS: Automated Backup Completed" email should be received.

B. Checking the Recovery Process (recovery_utility.py)

Step

Location

Command / Action

Verification Result

Integrity

Console Output

Watch the recovery script output during Step 4.

Reliability: Must display ✅ INTEGRITY CHECK SUCCESS for restoration to proceed.

Restored Files

/tmp/restored_files/

ls -R /tmp/restored_files/

Final Success: Your original source_data folder and its contents should be fully restored here.

🚀 Usage

1. Run the Backup Script (backup_core.sh)

This executes the full 8-step security and transfer pipeline:

# Ensure scripts are executable
chmod +x backup_core.sh recovery_utility.py

# Run the complete backup process
./backup_core.sh




💡 Note: On the first run, you will be prompted for your Private Key Passphrase to encrypt the file.

2. Automate Scheduling (cron)

To run the backup unattended every day at 3:00 AM:

Open the crontab editor: crontab -e

Paste the job line (ensure the path is correct):

0 3 * * * /home/linux01/Desktop/Automated_Backup_System/backup_core.sh > /dev/null 2>&1




3. Run Recovery (recovery_utility.py)

This utility retrieves the backup, runs the integrity check, and restores files:

./recovery_utility.py




🔑 Input Required: The script will first show an interactive menu to select the backup version, and then prompt for your Private Key Passphrase to decrypt the data.
