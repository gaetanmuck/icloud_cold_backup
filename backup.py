import os
from pyicloud import PyiCloudService
from backup_files import backup_files
from backup_photos import backup_photos
import click

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

# If connection requires 2FA, ask for code. 
if api.requires_2fa:
    verification_code = input("Verification code: ")
    result = api.validate_2fa_code(verification_code)
    if not result:
        print("Verification failed")
        exit(1)
    if not api.is_trusted_session:
        print("Session is not trusted. Requesting trust...")
        result = api.trust_session()
        print("Session trust result %s" % result)
elif api.requires_2sa:
    print("Two-step authentication required. Your trusted devices are:")
    devices = api.trusted_devices
    for i, device in enumerate(devices):
        print("  %s: %s" % (i, device.get('deviceName', "SMS to %s" % device.get('phoneNumber'))))
    device = click.prompt('Which device would you like to use?', default=0)
    device = devices[device]
    if not api.send_verification_code(device):
        print("Failed to send verification code")
        exit(1)
    code = click.prompt('Please enter validation code')
    if not api.validate_verification_code(device, code):
        print("Failed to verify verification code")
        exit(1)

# Backup Files
print('===== Backing iCloud Drive on the specified location =====')
backup_files(api, disk_path)
print('> iCloud Drive has correctly been backed up on disk.')

# Backup Photos
print('===== Backing iCloud photos on the specified location =====')
backup_photos(api, disk_path)
print('> iCloud Photos has correctly been backed up on disk.')