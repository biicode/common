import os
import fnmatch
import re
from biicode.common.exception import BiiException
from biicode.common.model.blob import Blob
from biicode.common.utils.bii_logging import logger


def save_blob_if_modified(path, blob):
    '''save the file, but avoid touching it if the contents have not been modified. Useful
    e.g. for CMakeLists files. It uses blob to avoid CRLF issues'''
    try:
        old_content = Blob(load(path), blob.is_binary)
    except:
        old_content = None
    if blob != old_content:
        logger.debug('{0} has changed or was created'.format(path))
        save(path, blob.load)
        return True
    return False


def get_visible_files_recursive(path):
    '''Returns all os visible files from path and it's subdirectories'''

    includes = ['.bii']
    excludes = ['.*']
    includes = r'|'.join([fnmatch.translate(x) for x in includes])
    excludes = r'|'.join([fnmatch.translate(x) for x in excludes]) or r'$.'
    vfiles = []
    for root, dirs, files in os.walk(path):
        # exclude dirs
        dirs[:] = [d for d in dirs \
                   if not re.match(excludes, d) or re.match(includes, d)]
        dirs[:] = [os.path.join(root, d) for d in dirs]
        # exclude/include files
        files = [f for f in files if not re.match(excludes, f)]
        files = [os.path.normpath(os.path.join(root, f)) for f in files]
        vfiles = vfiles + files
    return vfiles


def save(path, binary_content):
    '''
    Saves a file with given content
    Params:
        path: path to write file to
        binary_content: contents to save in the file
    '''
    try:
        os.makedirs(os.path.dirname(path))
    except:
        pass

    with open(path, 'wb') as handle:
        handle.write(binary_content)


def load(path, size=None):
    '''Loads a file content'''
    try:
        with open(path, 'rb') as handle:
            if size is None:
                size = -1
            return handle.read(size)
    except UnicodeDecodeError as e:
        raise BiiException("Error reading file %s : %s" % (path, e))


def resource_path(base_path, rel_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    import sys
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    return os.path.join(getattr(sys, '_MEIPASS', base_path), rel_path)


def load_resource(base_path, rel_path):
    return load(resource_path(base_path, rel_path))


def get_files(root, pattern):
    '''retrieves the relative file names of files whose filename matches a glob pattern'''
    vfiles = [f for f in fnmatch.filter(os.listdir(root), pattern)]
    return vfiles


def fix_os_separator(path):
    if os.sep == "/":
        return path.strip().replace("\\", os.sep)
    else:
        return path.strip().replace("/", os.sep)


def search_and_replace(path, token, replacement):
    '''Performs inline search and replace in given file'''
    c = load(path)
    assert token in c, "%s not found in %s" % (token, c)
    c = c.replace(token, replacement)
    save(path, c)


def rename_file(file_path, new_name):
    """Renames a file"""
    path, _ = os.path.split(file_path)
    new_file_name = os.path.join(path, new_name)
    os.rename(file_path, new_file_name)


def get_files_recursive(root, pattern):  
    '''retrieves the relative file names of files whose filename matches a glob pattern'''
    for path, _, files in os.walk(root):  
        for filename in fnmatch.filter(files, pattern):
            if(path == root):  # this case is to avoid the inclusion of ./ before the file name
                yield filename
            else:
                yield os.path.normpath(os.path.join(os.path.relpath(path, root), filename))


def is_binary_string(bytes_to_check):
    """
    :param bytes: A chunk of bytes to check.
    :returns: True if appears to be a binary, otherwise False.
    """
    # Uses a simplified version of the Perl detection algorithm,
    # based roughly on Eli Bendersky's translation to Python:
    # http://eli.thegreenplace.net/2011/10/19/perls-guess-if-file-is-text-or-binary-implemented-in-python/

    # This is biased slightly more in favour of deeming files as text
    # files than the Perl algorithm, since all ASCII compatible character
    # sets are accepted as text, not just utf-8

    def _printable_extended_ascii():
        printable_extended_ascii = b'\n\r\t\f\b'
        if bytes is str:
            # Python 2 means we need to invoke chr() explicitly
            printable_extended_ascii += b''.join(map(chr, range(32, 256)))
        else:
            # Python 3 means bytes accepts integer input directly
            printable_extended_ascii += bytes(range(32, 256))
        return printable_extended_ascii

    # Empty files are considered text files
    if not bytes_to_check:
        return False

    # Check for NUL bytes first
    if b'\x00' in bytes_to_check:
        return True

    # Now check for a high percentage of ASCII control characters
    # Binary if control chars are > 30% of the string
    control_chars = bytes_to_check.translate(None, _printable_extended_ascii())
    nontext_ratio = float(len(control_chars)) / float(len(bytes_to_check))
    return nontext_ratio > 0.3
