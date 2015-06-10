from biicode.common.edition.type_filter import TypeFilter
from biicode.common.model.blob import Blob
from biicode.common.utils.bii_logging import logger
from biicode.common.edition.block_holder import BlockHolder
from biicode.common.model.resource import Resource
from biicode.common.model.cells import SimpleCell
from biicode.common.model.content import Content
from biicode.common.edition import changevalidator
from biicode.common.model.brl.block_name import BlockName


def checkin_block_files(hive_holder, block_name, files, biiout):
    '''
    Params:
        hive_holder: ProjectHolder
        block_name: BlockName
        files: {cell_name: content}
        processor_changes: ProcessorChanges
        biiout: biiout
    '''
    block_name = BlockName(block_name)
    types_blobs = obtain_types_blobs(files)  # {cell_name: (TYPE, Content/CellType/None)}
    # FIXME: What happens if merge result is larger than individual files, reject???
    changevalidator.remove_large_cells(types_blobs, biiout)
    try:
        block_holder = hive_holder[block_name]
    except KeyError:
        block_holder = BlockHolder(block_name, [])
        hive_holder.add_holder(block_holder)

    for cell_name, (biitype, blob) in types_blobs.iteritems():
        block_cell_name = block_name + cell_name
        cell = SimpleCell(block_cell_name, biitype)
        try:
            resource = block_holder[cell_name]
        except KeyError:
            content = Content(block_cell_name, load=blob)
        else:
            content = resource.content
            if content is None or blob != content.load:
                content = Content(block_cell_name, load=blob)
            else:
                content.set_blob(blob)

        resource = Resource(cell, content)
        block_holder.add_resource(resource)

    for cell_name, resource in block_holder.resources.items():
        if cell_name not in types_blobs:
            block_holder.delete_resource(cell_name)


def checkin_files(hive_holder, settings, files, biiout):
    '''
    Params:
        hive_holder: ProjectHolder
        files: dict{BlockCellName: Item (str or bytes loaded from file)}
        biiout: biiout
    Returns: ProcessorChanges
    '''
    logger.debug("----------- checkin  ---------------")
    hive_holder.settings = settings

    if files is None:
        return

    block_files = {}
    for block_cell_name, filecontent in files.iteritems():
        block_files.setdefault(block_cell_name.block_name,
                               {})[block_cell_name.cell_name] = filecontent

    for block_name, files in block_files.iteritems():
        checkin_block_files(hive_holder, block_name, files, biiout)

    for block_holder in hive_holder.block_holders:
        if block_holder.block_name not in block_files:
            hive_holder.add_holder(BlockHolder(block_holder.block_name, []))

    hive_holder.delete_empty_blocks()


def obtain_types_blobs(files):
    """files: dict{BlockCellName: Item (str or bytes loaded from file)}
    return: {BlockCellName: (BiiType, Blob)}
    """
    tree = {}
    for block_cell_name, filecontent in files.iteritems():
        tokens = block_cell_name.split('/')
        base_tree = tree
        for token in tokens[:-1]:
            base_tree.setdefault(token, {})
            base_tree = base_tree[token]
        base_tree[tokens[-1]] = block_cell_name, filecontent

    result = {}
    apply_types(tree, TypeFilter(), result)
    return result


def apply_types(base_tree, current_types, result):
    '''
    Params:
        base_tree: {block_name: (CellName, content_str)}
        current_types: TypeFilter
        result: dict
    '''
    types_resource = base_tree.get('types.bii')
    if types_resource:
        types_filter = TypeFilter.loads(types_resource[1])
        current_types = current_types + types_filter
    for value in base_tree.itervalues():
        if isinstance(value, dict):
            base_tree = value
            apply_types(base_tree, current_types, result)
        else:
            block_cell_name, filecontent = value
            bii_type = _get_type_cell(filecontent, current_types, block_cell_name)
            blob = Blob(filecontent, is_binary=bii_type.is_binary())
            result[block_cell_name] = bii_type, blob


def _get_type_cell(filecontent, type_filter, cell_name):
    from biicode.common.model.bii_type import UNKNOWN
    bii_type = type_filter.type(cell_name)
    if bii_type == UNKNOWN:
        bii_type = bii_type.from_content(filecontent)
    return bii_type
