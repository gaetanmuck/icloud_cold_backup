import os
from datetime import datetime, timezone
import gmpykit as kit

eta = kit.Eta()

def __scan_icloud(api):    
    keys = set()
    photos = []
    total_size = 0

    for photo in api.photos.all:
        key = f'{photo.filename} - {int(photo.created.timestamp())} - {photo.size}'

        keys.add(key)
        photos.append({
            'path': photo.filename,
            'size': photo.size,
            'key': key,
            'obj': photo
        })

        total_size += photo.size
        print(f'Exploring iCloud Photos (this could take some minutes) ... {len(photos)} photos found ({kit.readable_bytes(total_size)})', end='          \r')

    print(f'> iCloud Photos explored, {len(photos)} photos found ({kit.readable_bytes(total_size)})                                                                                 ')
    return keys, photos


def __scan_disk(path):
    if not os.path.exists(path + '/photos'): 
        print('Nothing found on disk about photos backup, initializing...')
        os.mkdir(path + '/photos')
        return set(), []

    keys = set()
    photos = []
    total_size = 0

    for photo in os.listdir(path + '/photos/'):
        photo_path = path + '/photos/' + photo
        date = int(os.path.getmtime(photo_path))
        size = os.stat(photo_path).st_size
        key = f'{photo} - {date} - {size}'

        keys.add(key)
        photos.append({
            'path': photo_path,
            'size': size,
            'key': key
        })

        total_size += size
        print(f'Exploring disk photos ... {len(photos)} photos found ({kit.readable_bytes(total_size)})', end='          \r')

    print(f'> Disk photos explored, {len(photos)} photos found ({kit.readable_bytes(total_size)})                                                                                 ')
    return keys, photos



def backup_photos(api, backup_path):

    keys_icloud, photos_icloud = __scan_icloud(api)
    keys_disk, photos_disk = __scan_disk(backup_path)

    # DISK DELETION

    nb_deleted = 0

    if not len(photos_disk) == 0:
        eta.begin(len(photos_disk), '> Verifying photos on disk')
        for photo in photos_disk:

            # If photo key is not in the icloud set, then it has been updated, renamed or deleted
            if photo['key'] not in keys_icloud:
                path = photo['path']

                # Delete the photo
                os.remove(path)
                nb_deleted += 1

            eta.iter()
        eta.end()
        print(f'> {nb_deleted} photos have been pruned from disk')
    else:
        print(f'> No photos are currently on disk')

    # DISK CREATION

    # First list all items to create (so that the ETA is accurate)
    to_create = []
    eta.begin(len(photos_icloud), '> List all photo that need to be added to backup')
    for photo in photos_icloud:
        if photo['key'] not in keys_disk: 
            to_create.append(photo)
        eta.iter()
    eta.end()
    to_create = list(filter(lambda photo: photo['size'] != 0 and photo['size'] != None, to_create))
    total_photos_size = sum(list(map(lambda photo: photo['size'] if photo['size'] else 0, to_create)))
    print(f'> {len(to_create)} photos need to be downloaded and saved on disk ({kit.readable_bytes(total_photos_size)})')

    if len(to_create) != 0:
        # Then download and write on disk all files that need creation
        eta.begin(total_photos_size, '> Downloading and writing photos on disk')
        saved_size = 0
        for photo in to_create:

            # Download the photo in memory
            download = photo['obj'].download()

            # Download and write the photo on disk
            photo_path = backup_path + '/photos/' + photo['obj'].filename
            with open(photo_path, 'wb') as file_out:
                file_out.write(download.raw.read())
                saved_size += photo['size']

            # Set the modification date so that it matches the one on iCloud
            os.utime(photo_path, (int(photo['obj'].created.timestamp()), int(photo['obj'].created.timestamp())))

            eta.iter(saved_size)
        eta.end()
    else:
        print('> Nothing to add on disk')