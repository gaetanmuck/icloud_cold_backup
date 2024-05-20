import os
from datetime import datetime
from pathlib import Path
from functools import reduce
from shutil import copyfileobj  
import gmpykit as kit

eta = kit.Eta()


def __deref(data, keys):
    return reduce(lambda d, key: d[key], keys, data)


def __list_folder_icloud(path, folder, found_nb=0, found_size=0):
    keys = set()
    files = []

    total_nb = found_nb
    total_size = found_size

    for file_name in folder.dir():
        file = folder[file_name]
        if file.type == 'file':
            filepath = path + file_name
            filedate = file.date_modified.strftime("%Y%m%d%H%M%S")
            key = f'{filepath} - {filedate} - {file.size}'

            keys.add(key)
            files.append({
                'path': filepath,
                'size': file.size,
                'key': key
            })

            total_nb += 1
            total_size += file.size if file.size else 0
            print(f'Exploring iCloud drive (this could take some minutes) ... {total_nb} files found ({kit.readable_bytes(total_size)})', end='          \r')
        else:
            keys_, files_, total_nb, total_size = __list_folder_icloud(path + file_name + '/', file, total_nb, total_size)
            keys.update(keys_)
            files += files_
    
    return keys, files, total_nb, total_size


def __scan_icloud(api):
    keys, files, nb, size = __list_folder_icloud('/', api.drive)
    print(f'> iCloud Drive explored, {nb} files found ({kit.readable_bytes(size)})                                                                                 ')
    return keys, files


def __list_folder_disk(path, relative_path, found_nb=0, found_size=0):
    keys = set()
    files = []

    total_nb = found_nb
    total_size = found_size

    for file in os.listdir(path):
        if os.path.isdir(path + '/' + file):
            keys_, files_, total_nb, total_size = __list_folder_disk(path + file + '/', relative_path + file + '/', total_nb, total_size)
            keys.update(keys_)
            files += files_
        else: 
            date = datetime.fromtimestamp(os.path.getmtime(path + file)).strftime("%Y%m%d%H%M%S")
            size = os.stat(path + file).st_size
            key = f'{relative_path + file} - {date} - {size}'
            
            keys.add(key)
            files.append({
                'path': path + file,
                'size': size,
                'key': key,
            })
            total_nb += 1
            total_size += size
            print(f'Exploring disk drive ... {total_nb} files found ({kit.readable_bytes(total_size)})', end='          \r')

    return keys, files, total_nb, total_size
         

def __scan_disk(path):
    if not os.path.exists(path + '/drive'): 
        print('Nothing found on disk about drive backup, initializing...')
        os.mkdir(path + '/drive')
        return set(), []
    
    keys, files, nb, size = __list_folder_disk(path + '/drive/', '/')
    print(f'> Disk drive explored, {nb} files found ({kit.readable_bytes(size)})                                                                                 ')

    return keys, files



def backup_files(api, backup_path):

    keys_icloud, files_icloud = __scan_icloud(api)
    keys_disk, files_disk = __scan_disk(backup_path)

    # DISK DELETION

    nb_deleted = 0

    if not len(files_disk) == 0:
        eta.begin(len(files_disk), '> Verifying files on disk')
        for file in files_disk:

            # If file key is not in the icloud set, then it has been updated, renamed or deleted
            if file['key'] not in keys_icloud:
                path = file['path']

                # Delete the file
                os.remove(path)
                nb_deleted += 1

                # Delete all empty parents
                try: os.removedirs(path[0:path.rfind('/')])
                except: pass

            eta.iter()
        eta.end()
        print(f'> {nb_deleted} files have been pruned from disk')
    else:
        print(f'> No files are currently on disk')

    # DISK CREATION

    # First list all items to create (so that the ETA is accurate)
    to_create = []
    eta.begin(len(files_icloud), '> List all files that need backup')
    for file in files_icloud:
        if file['key'] not in keys_disk: 
            to_create.append(file)
        eta.iter()
    eta.end()
    to_create = list(filter(lambda file: file['size'] != 0 and file['size'] != None, to_create))
    total_files_size = sum(list(map(lambda file: file['size'] if file['size'] else 0, to_create)))
    print(f'> {len(to_create)} files need to be downloaded and saved on disk ({kit.readable_bytes(total_files_size)})')

    if len(to_create) != 0:
        # Then download and write on disk all files that need creation
        eta.begin(total_files_size, '> Downloading and writing files on disk')
        saved_size = 0
        for file in to_create:
            # Get the icloud file object
            icloud_path = file['path'][1:].split('/')
            icloud_file = __deref(api.drive, icloud_path)

            # Create the path on disk for the specific file
            file_disk_path = backup_path + '/drive' + file['path']
            Path(file_disk_path[0:file_disk_path.rfind('/')]).mkdir(parents=True, exist_ok=True)

            # Download and write the file on disk
            with icloud_file.open(stream=True) as response:
                with open(file_disk_path, 'wb') as file_out:
                    copyfileobj(response.raw, file_out)
                    saved_size += file['size'] if file['size'] else 0

            # Set the modification date so that it matches the one on iCloud
            os.utime(file_disk_path, (int(icloud_file.date_modified.timestamp()), int(icloud_file.date_modified.timestamp())))

            eta.iter(saved_size)
        eta.end()
    else:
        print('> Nothing to add on disk')
    