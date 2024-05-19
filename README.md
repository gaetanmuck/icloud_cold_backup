# iCloud Cold Backup

![GitHub all releases](https://img.shields.io/github/downloads/gaetanmuck/icloud_cold_backup/total)

A python script to save icloud content on a hard drive.
Only apply modifications from last execution.

Supported: 
- iCloud Drive
- iCloud Photos

## Usage

### Environment Variables

**APPLE_ID**

Create an environment variable named "APPLE_ID" with the Apple identifier you need to save the iCloud from.

**APPLE_PWD**

Create an environment variable named "APPLE_PWD" with the password associated to the Apple account.
This password will only be used to connect to iCloud API. 
Do not trust me, check the code!

**BACKUP_PATH**

Create an environment variable named "BACKUP_PATH" for the place where you want your backup to be stored.
eg: you have a Hard Drive Disk you want to use for this purpose named "HDD", then it should be: `BACKUP_PATH=/Volumes/HDD`

### Dependencies

- **gmpykit**: Personal Python toolbox, https://github.com/gaetanmuck/gmpykit
- **pyicloud**: iCloud API Wrapper, https://github.com/picklepete/pyicloud

## Getting started

1. Clone the repository: `git clone https://github.com/gaetanmuck/icloud_cold_backup.git` (suppose you did that here: `~`)
2. Install dependencies: `pip install gmpykit pyicloud`
3. Set all three environment variables
4. Create an alias in your RC file: `echo "alias backup='python3 ~/icloud_cold_backup/backup.py'" >> ~/.zshrc` (suppose you use ZSH)
5. Restart your Terminal (or run `source ~/.zshrc`)
6. Run `backup`

# Thanks

If you find value in this script and would like to show your support, you can [Buy Me A Coffee](https://www.buymeacoffee.com/gaetanmuck), it would be grateful.
