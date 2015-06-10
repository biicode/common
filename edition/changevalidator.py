from biicode.common.conf import MEGABYTE
from biicode.common.conf import (BII_FILE_SIZE_LIMIT, BII_MAX_BLOCK_SIZE,
                                 BII_BLOCK_NUMFILES_LIMIT)


def text_for_megabytes(bytes_amount):
    int_mb = int(bytes_amount / MEGABYTE)
    return "%i MB" % int_mb

BII_FILE_SIZE_LIMIT_STR = text_for_megabytes(BII_FILE_SIZE_LIMIT)  # Max file size
BII_MAX_BLOCK_SIZE_STR = text_for_megabytes(BII_MAX_BLOCK_SIZE)


def remove_large_cells(files, biiout):
    '''
    Filter changes by size
    Keyword arguments:
    '''
    modified = files.copy()
    for name, (_, blob) in modified.iteritems():
        if blob.size >= BII_FILE_SIZE_LIMIT:
            biiout.warn("File %s is bigger "
                        "than %s: discarded" % (name, BII_FILE_SIZE_LIMIT_STR))
            del files[name]


def check_block_size(block_holder, biiout):
    """Check num of files and the block size reading size of files on filesystem
    Params:
        hive_holder: ProjectHolder
        block: BlockName
        biiout: biiout
    """
    block = block_holder.block_name
    if len(block_holder._resources) > BII_BLOCK_NUMFILES_LIMIT:
        biiout.warn("Block '%s' has reached the limitation of %s num files per block. "
                         "Reduce number of "
                         "files before publish" % (block, BII_BLOCK_NUMFILES_LIMIT))

    size = sum([r.content.load.size for r in block_holder.simple_resources])
    if size > BII_MAX_BLOCK_SIZE:
        biiout.warn("Block '%s' has reached max size of %s. Reduce size before publish"
                         % (block, BII_MAX_BLOCK_SIZE_STR))
        return False
    return True
