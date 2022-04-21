# Initial code stolen from Enstore

MAX_FILE_SIZE = 2 ** 30 * 8 - 1


def makedev(major, minor):
    return (major << 8) | minor


def create_header(inode, mode, uid, gid, nlink, mtime, filesize: int,
                  major, minor, rmajor, rminor, filename: str) -> bytes:
    """
    Crete the header record
    """

    # Files greater than 8GB are not allowed
    if filesize > MAX_FILE_SIZE:
        msg = "Files are limited to %s bytes and your %s has %s bytes" % (MAX_FILE_SIZE, filename, filesize)
        raise RuntimeError(msg)
    fname = filename
    fsize = filesize
    # Set the mode to something that works on all machines!
    if ((mode & 0o777000) != 0o100000) & (filename != "TRAILER!!!"):
        mode = 0o100664

    # make all filenames relative - strip off leading slash
    if fname[0] == "/":
        fname = fname[1:]
    dev = makedev(major, minor)
    rdev = makedev(rmajor, rminor)
    header = "070707%06o%06lo%06lo%06lo%06lo%06lo%06o%011lo%06lo%011lo%s\0" % \
             (dev & 0xffff, inode & 0xffff, mode & 0xffff,
              uid & 0xffff, gid & 0xffff, nlink & 0xffff,
              rdev & 0xfff, mtime, (len(fname) + 1) & 0xffff,
              fsize, fname)
    return bytes(header, 'utf-8')


# create  header + trailer
def headers(file_info):
    inode = file_info.get('inode', 0)
    if inode is None:
        inode = 0
    mode = file_info.get('mode', 0)
    uid = file_info.get('uid', 0)
    gid = file_info.get('gid', 0)
    nlink = file_info.get('nlink', 1)
    mtime = file_info.get('mtime', 0)
    filesize = file_info.get('size_bytes', 0)
    major = file_info.get('major', 0)
    minor = file_info.get('minor', 0)
    rmajor = file_info.get('rmajor', 0)
    rminor = file_info.get('rminor', 0)
    filename = file_info.get('pnfsFilename', '???')

    header = create_header(inode, mode, uid, gid, nlink, mtime, filesize,
                           major, minor, rmajor, rminor, filename)

    # create the trailer as well
    trailer = create_header(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, "TRAILER!!!")
    # Trailers must be rounded to 512 byte blocks.
    pad: int = (len(header) + len(trailer) + filesize) % 512
    if pad:
        pad = 512 - pad
        trailer = trailer + b'\0' * pad
    return header, trailer
