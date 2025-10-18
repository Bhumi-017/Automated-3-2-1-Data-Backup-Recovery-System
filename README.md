## 🛡️ Automated 3-2-1 Data Backup & Recovery System

This project engineers a **robust, self-auditing data backup solution** for Linux environments.  
It automates **compression**, **asymmetric encryption (GPG Key Pair)**, and **scheduled transfer** to ensure data survivability following the **3-2-1 backup rule**.

It demonstrates mastery of **system automation**, **security protocols**, and **data integrity verification**.

---

**📁 Project Setup**

To ensure all absolute paths in the scripts work correctly, create a dedicated project folder inside your user’s home directory (`~`).

**🧱 Create the Main Project Directory**
```bash
mkdir -p ~/Desktop/Automated_Backup_System
cd ~/Desktop/Automated_Backup_System
```
**📂 File Placement**
Place backup_core.sh and recovery_utility.py directly inside the Automated_Backup_System folder.

Create the following folders:

1. source_data/ — contains files to back up (e.g., test_file.txt)

2. network_target_test/ — simulates your network backup location

**✨ Key Features & Security Protocols**

| **Focus Area** | **Feature Implemented** | **Security / Reliability** |
|----------------|--------------------------|-----------------------------|
| **3-2-1 Compliance** | Triple Copy Transfer | Local Drive (Copy 1), Network Target (Copy 2 via `rsync`), and Offsite Cloud (Copy 3 via `rclone`) |
| **Encryption** | GPG Key Pair (Public/Private) | Uses asymmetric encryption — data encrypted with Public Key, decrypted with Private Key Passphrase |
| **Integrity** | SHA256 Verification | Ensures data isn’t corrupted during compression or transfer |
| **Robustness** | Automated Auditing | Logs every action and sends email alerts upon success/failure |
| **User Experience** | Interactive Recovery | Lists available backups and restores chosen version |

**🛠️ Prerequisites**

Before running the system, ensure the following utilities are installed on Kali/Ubuntu/Debian:

1. GPG (GnuPG) — for encryption (usually pre-installed)

2. rsync — for network transfers (usually pre-installed)

3. rclone — for offsite cloud transfer

4. mailutils — for email notifications
   
**📦 Install Requirements**
```bash
sudo -v
curl https://rclone.org/install.sh | sudo bash
sudo apt update && sudo apt install mailutils -y
```
**⚙️ Configuration (One-Time Setup)**
🔑 1. Generate and Register Your GPG Key
| **Action** | **Command** | **Note** |
|-------------|-------------|----------|
| **Generate Keys** | `gpg --full-generate-key` | Choose **RSA 4096 bits** and set a strong **Private Key Passphrase** |
| **Find Key ID** | `gpg --list-keys` | Copy your **8–16 character Key ID** — this becomes your `RECIPIENT_ID` |

☁️ 2. Configure the Cloud Remote (rclone)
Run:

```bash
rclone config
```
Follow the prompts to select your cloud provider (e.g., Google Drive).
Note the remote name you give — you’ll use it later (e.g., my_gdrive).

🧩 3. Update Script Variables
Open backup_core.sh and replace the placeholders in the Configuration Variables section:

| **Variable** | **Placeholder** | **Your Value** | **Purpose** |
|---------------|------------------|----------------|--------------|
| **RECIPIENT_ID** | `[YOUR_GPG_KEY_ID]` | Paste your actual **GPG Key ID** | Required for encryption |
| **ALERT_EMAIL** | `linux01@localhost` | Your real **email address** | Required for alerts |
| **CLOUD_REMOTE** | `[YOUR_REMOTE_NAME]:Encrypted_Backups` | Example: `my_gdrive:Encrypted_Backups` | For offsite cloud backup |

**✅ Verification & Auditing**
After running your backup or recovery scripts, use these checks to confirm success.

🧩 A. Checking the Backup Process (backup_core.sh)
| **Step** | **Location** | **Command / Action** | **Expected Result** |
|-----------|---------------|----------------------|----------------------|
| **Logging** | `/tmp/` | `ls -l /tmp/backup_log_*.txt` | A new log file confirms all steps ran |
| **Copy 2 (Network)** | `./network_target_test/` | `ls -l network_target_test/*.gpg` | Encrypted `.gpg` file present |
| **Copy 3 (Cloud)** | Your Cloud Drive | Check manually | Encrypted backup uploaded |
| **Alerts** | Mailbox | Check configured email | “SUCCESS: Automated Backup Completed” received |

🧩 B. Checking the Recovery Process (recovery_utility.py)
| **Step** | **Location** | **Command / Action** | **Expected Result** |
|-----------|---------------|----------------------|----------------------|
| **Integrity** | Console | Watch terminal output | Displays ✅ **INTEGRITY CHECK SUCCESS** |
| **Restored Files** | `/tmp/restored_files/` | `ls -R /tmp/restored_files/` | Source files restored successfully |

**🚀 Usage**
▶️ 1. Run the Backup Script
```bash
chmod +x backup_core.sh recovery_utility.py
./backup_core.sh
```
💡 On first run, you’ll be prompted for your Private Key Passphrase.

⏰ 2. Automate with Cron (Daily at 3:00 AM)
```bash
crontab -e
```
Add this line:

```bash
0 3 * * * /home/linux01/Desktop/Automated_Backup_System/backup_core.sh > /dev/null 2>&1
```
💾 3. Run the Recovery Utility
```bash
./recovery_utility.py
```
Displays all available backups

Prompts for your Private Key Passphrase

Verifies integrity before restoring

**🧠 System Summary**

| **Function** | **Script / Folder** | **Location** | **Description** |
|---------------|----------------------|----------------|------------------|
| **Backup Engine** | `backup_core.sh` | Root project folder | Automates compression, encryption, and transfer |
| **Recovery Utility** | `recovery_utility.py` | Root project folder | Handles decryption, integrity check, and restore |
| **Local Source** | `source_data/` | Inside project | Contains files to be backed up |
| **Network Target** | `network_target_test/` | Inside project | Simulates external storage or network share |
| **Logs** | `/tmp/backup_log_*.txt` | System temp directory | Stores detailed process records for auditing |

**🧩 Tech Stack**

Bash (Shell Scripting) — core automation engine

Python — recovery utility and integrity verification

GPG — asymmetric encryption (RSA 4096-bit)

rsync — local and network-efficient transfers

rclone — secure offsite cloud replication

cron — scheduling automation

mailutils — automated email notifications

**🎯 Conclusion**

This system offers secure, automated, and fully auditable backups following the 3-2-1 rule. With encryption, multi-location storage, integrity checks, and interactive recovery, it ensures your data is always protected, accessible, and resilient—making backup and recovery reliable, repeatable, and hassle-free.
