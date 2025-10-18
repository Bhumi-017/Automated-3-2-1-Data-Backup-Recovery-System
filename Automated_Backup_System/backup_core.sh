#!/bin/bash

# --- Improvised Configuration Variables ---

# The user/key ID that will be able to decrypt the file.
# !!! CRITICAL: REPLACE '4A4A87C1' with your actual 8-character GPG Key ID !!!
RECIPIENT_ID="8BBB86ECC13A0A363BE80834EB54B7E2DFBC4CF1"

# Email address to send alerts to (must configure mailutils)
ALERT_EMAIL="boo946402@gmail.com"

# Project Directories
SOURCE_DIR="/home/linux01/Desktop/Automated_Backup_System/source_data"
STAGING_DIR="/tmp/backup_staging"
NETWORK_TARGET_DIR="/home/linux01/Desktop/Automated_Backup_System/network_target_test"

# rclone cloud configuration (3-2-1 Offsite Copy)
# NOTE: Replace 'cloud_offsite' with the name you configured in 'rclone config'.
CLOUD_REMOTE="gdrive_new:Encrypted_Backups" 

# --- Setup and Naming ---
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
LOG_FILE="/tmp/backup_log_$TIMESTAMP.txt"
ARCHIVE_NAME="backup_$TIMESTAMP.tar.gz"
ENCRYPTED_ARCHIVE_NAME="backup_$TIMESTAMP.tar.gz.gpg"
STATUS="SUCCESS" # Initial status

# --- Logging Function (Robustness Improvisation) ---

log() {
    echo "$(date +%H:%M:%S) - $1" | tee -a "$LOG_FILE"
}

handle_error() {
    local exit_code=$1
    local step_name=$2
    STATUS="FAILURE"
    log "CRITICAL ERROR: $step_name failed with exit code $exit_code. Sending alert." 
    
    # Send Failure Email
    (
        echo "Subject: CRITICAL: Automated Backup FAILED"
        echo "To: $ALERT_EMAIL"
        echo "MIME-Version: 1.0"
        echo "Content-Type: text/plain; charset=\"UTF-8\""
        echo "Date: $(date -R)"
        echo ""
        echo "The Automated Backup process failed during the '$step_name' step."
        echo ""
        cat "$LOG_FILE"
    ) | /usr/sbin/sendmail -t
    
    # Final cleanup before exit
    rm -rf "$STAGING_DIR" 
    exit 1
}

# --- Execution ---

log "Starting resilient data backup at $TIMESTAMP..."

# Create necessary directories
mkdir -p "$NETWORK_TARGET_DIR"
mkdir -p "$STAGING_DIR"

# 1. Archive the source data (temporarily to a new, clean folder inside STAGING)
# This prevents the "Cannot stat" error by archiving a clean, dedicated folder structure.
TEMP_ARCHIVE_DIR="$STAGING_DIR/ARCHIVE_ROOT"
mkdir -p "$TEMP_ARCHIVE_DIR"

log "Step 1: Compressing $SOURCE_DIR."
# Create a single compressed archive of the SOURCE_DIR inside the temporary root
tar -czf "$TEMP_ARCHIVE_DIR/data.tar.gz" -C "$(dirname "$SOURCE_DIR")" "$(basename "$SOURCE_DIR")" || handle_error $? "Compression"

# 2. Calculate SHA256 Checksum (Reliability Improvisation)
log "Step 2: Calculating SHA256 integrity checksum..."
# Calculate checksum of the temporary data archive
SHA256_CHECKSUM=$(sha256sum "$TEMP_ARCHIVE_DIR/data.tar.gz" | awk '{print $1}')
echo "$SHA256_CHECKSUM" > "$TEMP_ARCHIVE_DIR/checksum_$TIMESTAMP.txt"
log "Checksum calculated: $SHA256_CHECKSUM"

# 3. Final Archiving (Archive the ROOT folder containing data and checksum)
log "Step 3: Finalizing archive including checksum."
# This creates the final .tar.gz file containing both the data archive and the checksum file.
tar -czf "$STAGING_DIR/$ARCHIVE_NAME" -C "$STAGING_DIR" ARCHIVE_ROOT || handle_error $? "Final Archiving"

# Cleanup temporary data folder
rm -rf "$TEMP_ARCHIVE_DIR"


# 4. Encrypt the Archive (Security Improvisation - Key Pair)
log "Step 4: Encrypting archive using GPG Key ID $RECIPIENT_ID."

# Encrypts using the recipient's public key; decryption requires the private key passphrase.
gpg --batch --yes --output "$STAGING_DIR/$ENCRYPTED_ARCHIVE_NAME" --encrypt --recipient "$RECIPIENT_ID" "$STAGING_DIR/$ARCHIVE_NAME" || handle_error $? "Encryption"

log "Encryption complete."

# 5. Secure Cleanup: Remove the unencrypted archive
log "Step 5: Removing unencrypted file from staging area."
rm -f "$STAGING_DIR/$ARCHIVE_NAME"

# 6. Transfer the Encrypted Archive (rsync to local network target - Copy 2)
log "Step 6: Transferring encrypted file to network target: $NETWORK_TARGET_DIR"

rsync -avz "$STAGING_DIR/$ENCRYPTED_ARCHIVE_NAME" "$NETWORK_TARGET_DIR/" || handle_error $? "rsync Transfer"

log "rsync Transfer complete."

# 7. Cloud Integration (rclone to offsite target - Copy 3)
log "Step 7: Uploading encrypted file to Cloud Offsite: $CLOUD_REMOTE"

# rclone command for robust, modern cloud transfer
rclone copy "$STAGING_DIR/$ENCRYPTED_ARCHIVE_NAME" "$CLOUD_REMOTE" || handle_error $? "rclone Cloud Transfer"

log "rclone Transfer complete. 3-2-1 achieved."


# 8. Final Cleanup
log "Step 8: Cleaning up encrypted file from staging."
rm -f "$STAGING_DIR/$ENCRYPTED_ARCHIVE_NAME"

# --- Final Logging and Alert ---
if [ "$STATUS" == "SUCCESS" ]; then
    log "Backup process finished successfully."
    
    # Send Success Email
    (
        echo "Subject: SUCCESS: Automated Backup Completed"
        echo "To: $ALERT_EMAIL"
        echo "MIME-Version: 1.0"
        echo "Content-Type: text/plain; charset=\"UTF-8\""
        echo "Date: $(date -R)"
        echo ""
        echo "The Automated Backup process completed successfully at $TIMESTAMP."
        echo "Log details:"
        echo ""
        cat "$LOG_FILE"
    ) | /usr/sbin/sendmail -t
fi

# Clean up the staging directory itself (just in case)
rm -rf "$STAGING_DIR"


