import os
import shutil
import biicode.common.test
from biicode.common.utils import file_utils as common_file_utils


def load(filepath):
    """Return binary load of given test resource."""
    abspath = file_path(filepath)
    with open(abspath, "rb") as f:
        return f.read()


def read(filepath):
    """Return system text content of given test resource."""
    abspath = file_path(filepath)
    with open(abspath, "r") as f:
        return f.read()


def write(file_, content):
    try:
        os.makedirs(os.path.split(file_)[0])
    except:
        pass
    with open(file_, "wb") as f:
        return f.write(content)

test_resources = os.path.join(os.path.dirname(biicode.common.test.__file__),
                              "resources/")


def append(content, dest):
    with open(dest, "a") as f:
        f.write(content)


def get_dir_files(path):
    """Returns a list of files within given test folder
    Paths are relative to test/resources/path"""
    abs_paths = common_file_utils.get_visible_files_recursive(file_path(path))
    base_path = os.path.join(test_resources, path)
    return [os.path.relpath(p, base_path) for p in abs_paths]


def file_path(name):
    """Return full path to given test resource. """
    return os.path.join(test_resources, name)


def copyFiles(container, dest_folder, files=None):
    '''Copies files from container to dst_folder, filtering by files if provided
    '''
    new_files = []
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    if not files:
        files = get_dir_files(container)

    for f in files:
        srcpath = file_path(os.path.join(container, f))
        dest = os.path.join(dest_folder, f)
        dst_subfolder = os.path.join(dest_folder, os.path.dirname(f))
        if not os.path.isdir(dst_subfolder):
            os.makedirs(dst_subfolder)
        if os.path.isdir(srcpath):
            shutil.copytree(srcpath, dest)
        else:
            shutil.copyfile(srcpath, dest)
        new_files.append(dest)
    return new_files

def copyFile(src, dst_folder, dst_name=None):
    '''Copies src file from test/resources folder to dst_folder
    renamed to dst_name if provided
    '''
    srcpath = file_path(src)
    if not dst_name:
        dst_name = os.path.split(src)[1]
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)
    dst = os.path.join(dst_folder, dst_name)
    shutil.copyfile(srcpath, dst)
    return dst


def createFile(name, dst_folder, content):
    path = os.path.join(dst_folder, name)
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)
    with open(path, 'w+') as f:
        f.write(content)
    return path


def removeFolderContents(path):
    '''Recursively deletes all content in given directory'''
    for root, dirs, files in os.walk(path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

def search_pattern_and_replace(path, pattern, replacement):
    '''Performs inline search and replace in given file'''
    import fileinput, re
    for line in fileinput.FileInput(path, inplace=1):
        line = re.sub(pattern, replacement, line)
        print line,  # DO NOT REMOVE THIS PRINT, it is necessary for replace to work


def copy_directory(origin, dest):
    shutil.copytree(origin, dest)
    return dest

import filecmp
import os.path


def are_dir_trees_equal(dir1, dir2):
    """
    Compare two directories recursively. Files in each directory are
    assumed to be equal if their names and contents are equal.

    @param dir1: First directory path
    @param dir2: Second directory path

    @return: True if the directory trees are the same and
        there were no errors while accessing the directories or files,
        False otherwise.
   """

    dirs_cmp = filecmp.dircmp(dir1, dir2)
    if len(dirs_cmp.left_only) > 0 or len(dirs_cmp.right_only) > 0 or \
        len(dirs_cmp.funny_files) > 0:
        return False
    (_, mismatch, errors) = filecmp.cmpfiles(
        dir1, dir2, dirs_cmp.common_files, shallow=False)
    if len(mismatch) > 0 or len(errors) > 0:
        return False
    for common_dir in dirs_cmp.common_dirs:
        new_dir1 = os.path.join(dir1, common_dir)
        new_dir2 = os.path.join(dir2, common_dir)
        if not are_dir_trees_equal(new_dir1, new_dir2):
            return False
    return True


def replace_content(folder, file_name, tag, tag_content):
    """ Replace content from folder/file_name of tag with tag content."""

    file_path = os.path.join(folder, file_name)
    content = read(file_path)
    content = content.replace(tag, tag_content)
    return write(file_path, content)
