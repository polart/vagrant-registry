import hashlib


def get_file_hash(afile, hasher, blocksize=65536):
    hasher = getattr(hashlib, hasher)()

    if afile.closed:
        afile.open()
    else:
        # In case file was already read, set the read cursor
        # to the start of the file
        afile.seek(0)

    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()
