import os
from pyicloud import PyiCloudService
from backup_files import backup_files
from backup_photos import backup_photos

# Input checking
if 'BACKUP_PATH' not in os.environ:
    print('[ERROR]: No backup path provided, you need to specify the backup location (eg. "BACKUP_PATH=/Volumes/HardDriveName")')
    exit()
if 'APPLE_ID' not in os.environ:
    print('[ERROR]: Environment variable missing: APPLE_ID (eg. "APPLE_ID=john.doe@example.com")')
    exit()
if 'APPLE_PWD' not in os.environ:
    print('[ERROR]: Environment variable missing: APPLE_PWD (eg. "APPLE_PWD=password")')
    exit()

# Parse params
apple_id = os.getenv('APPLE_ID')
apple_pwd = os.getenv('APPLE_PWD')
disk_path = os.getenv('BACKUP_PATH')

# Check backup path location
if not os.path.exists(disk_path):
    print(f'[ERROR]: BACKUP_PATH "{disk_path}" not found, have you plugged it in?')
    exit()

# Connect to iCloud API
api = PyiCloudService(apple_id, apple_pwd)

# Backup Files
print('===== Backing iCloud Drive on the specified location =====')
backup_files(api, disk_path)
print('> iCloud Drive has correctly been backed up on disk.')

# Backup Photos
print('===== Backing iCloud photos on the specified location =====')
backup_photos(api, disk_path)
print('> iCloud Photos has correctly been backed up on disk.')