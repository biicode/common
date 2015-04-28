from biicode.common.model.bii_type import BiiType, UNKNOWN

from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.cells import SimpleCell
from biicode.common.model.content import Content
from biicode.common.model.blob import Blob
from biicode.common.test import testfileutils
from biicode.common.model.resource import Resource
import os
import random
from biicode.common.edition.parsing.factory import parser_factory
from biicode.common.edition.block_holder import BlockHolder
from biicode.common.model.id import UserID
from biicode.common.utils.file_utils import load


def make_content(brl, lang=BiiType(UNKNOWN), read_file=True):
    '''Reads a test file as binary or systext depending on lang
    Parameters:
        brl: BlockCellName or ID
    '''
    if isinstance(lang, int):
        lang = BiiType(lang)
    binary = lang.is_binary()
    if isinstance(brl, basestring):
        name = '/'.join(brl.split('/')[1:])
        parser = parser_factory(lang, brl.split('/')[-1])
    if read_file:
        path = testfileutils.file_path(name)
        content = load(path)
        blob = Blob(content, is_binary=binary)
    else:
        blob = Blob("Blob example content", is_binary=binary)
    return Content(brl, blob, parser)


def make_too_big_content(brl, lang=BiiType(UNKNOWN)):
    blob_load = load(testfileutils.file_path("limits/largefile.txt"))
    blob = Blob(blob_load, is_binary=True)
    parser = parser_factory(lang, brl.cell_name)
    return Content(brl, blob, parser)


def make_variable_content(brl, lang=BiiType(UNKNOWN), up_limit=2048):
    '''Generates a content with variable size, from 0 byte to 2kb. Returns the content'''
    size = random.choice(range(up_limit))
    blob = Blob(generate_text(size), False)
    parser = parser_factory(lang, brl.cell_name)
    return Content(brl, blob, parser)


def generate_text(size):
    return bytearray(size)


def get_block_holder(block_cell_names, biitype=BiiType(UNKNOWN)):
    '''Given a working set, a list of resources and a biitype constant
     - Adds every resource to the working set and assign given type
     - Read test files from disk as binary or systext depending on given type and creates contents
     - Fills a wsHolder with given resources and created contents
    '''

    resources = []
    for name in block_cell_names:
        cell = SimpleCell(name, biitype)
        content = make_content(name, biitype)
        resources.append(Resource(cell, content))

    block_name = BlockCellName(iter(block_cell_names).next()).block_name
    return BlockHolder(block_name, resources)


def make_simple_cell(block_cell_name):
    if isinstance(block_cell_name, basestring):
        block_cell_name = BlockCellName(block_cell_name)
    cell = SimpleCell(block_cell_name)
    cell.type = BiiType.from_extension(block_cell_name.extension)
    return cell


def make_published_resource(block, block_cell_name):
    if isinstance(block_cell_name, basestring):
        moduleCellName = BlockCellName(block_cell_name)
    sr = SimpleCell(block_cell_name)
    sr.type = BiiType.from_extension(moduleCellName.extension)
    sr.ID = UserID(1) + 1 + 2
    return sr


def make_resource(name, hive, read_file=True):
    cell = make_simple_cell(name, hive)
    return Resource(cell=cell,
                    content=make_content(cell.ID, read_file=read_file))


def make_folder_resources(user, path):
    '''
    Creates a SimpleCell for every file in given path
    Returns the list of SimpleCell
    '''
    files = testfileutils.get_dir_files(path)
    return [BlockCellName('%s/%s' % (user, os.path.join(path, f))) for f in files]
