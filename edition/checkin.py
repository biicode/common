from biicode.common.utils.bii_logging import logger
from biicode.common.edition.block_holder import BlockHolder
from biicode.common.model.cells import SimpleCell
from biicode.common.model.content import Content
from biicode.common.edition import changevalidator
from biicode.common.edition.processors.processor_changes import ProcessorChanges
from biicode.common.model.brl.block_name import BlockName
from biicode.common.settings.settings import Settings
from biicode.common.model.resource import Resource
from biicode.common.edition.type_filter import TypeFilter
from biicode.common.model.blob import Blob


class CheckinManager(object):

    def __init__(self, hive_holder, settings, biiout):
        '''
        Params:
            hive_holder: HiveHolder
            settings: Settings
            biiout: biiout
        '''
        self.hive_holder = hive_holder
        self.settings = settings or Settings()
        self.biiout = biiout

    def checkin_files(self, files):
        '''
        Params:
            files: dict{BlockCellName: Item (str or bytes loaded from file)}
        Returns: ProcessorChanges
        '''
        logger.debug("----------- checkin  ---------------")
        hive = self.hive_holder.hive
        hive.settings = self.settings

        processor_changes = ProcessorChanges()
        if files is None:
            return processor_changes

        block_files = {}
        for block_cell_name, filecontent in files.iteritems():
            block_files.setdefault(block_cell_name.block_name,
                                   {})[block_cell_name.cell_name] = filecontent

        for block_name, files in block_files.iteritems():
            self.checkin_block_files(block_name, files, processor_changes)

        for block_holder in self.hive_holder.block_holders:
            if block_holder.block_name not in block_files:
                processor_changes.deleted.update(block_holder.block_cell_names)
                self.hive_holder.add_holder(BlockHolder(block_holder.block_name, []))

        self.hive_holder.delete_empty_blocks()
        hive.update(processor_changes)

        # Raises if max is overtaken
        changevalidator.check_hive_num_cells(hive)
        return processor_changes

    def checkin_block_files(self, block_name, files, processor_changes):
        '''
        Params:
            block_name: BlockName
            files: {cell_name: content}
            processor_changes: ProcessorChanges
        '''
        block_name = BlockName(block_name)
        normalize = self.settings.user.get("autocrlf", True)
        if not normalize:
            self.biiout.info("Skipping file normalizing")

        types_blobs = obtain_types_blobs(files, normalize)  # {cell_name: (TYPE, Content/CellType/None)}
        # FIXME: What happens if merge result is larger than individual files, reject???
        changevalidator.remove_large_cells(types_blobs, self.biiout)
        try:
            block_holder = self.hive_holder[block_name]
        except KeyError:
            block_holder = BlockHolder(block_name, [])
            self.hive_holder.add_holder(block_holder)

        for cell_name, (biitype, blob) in types_blobs.iteritems():
            block_cell_name = block_name + cell_name
            cell = SimpleCell(block_cell_name, biitype)
            try:
                resource = block_holder[cell_name]
            except KeyError:
                content = Content(block_cell_name, load=blob)
                processor_changes.upsert(block_cell_name, content)
            else:
                content = resource.content
                if content is None or blob != content.load:
                    content = Content(block_cell_name, load=blob)
                    processor_changes.upsert(block_cell_name, content)
                else:
                    content.set_blob(blob)

            resource = Resource(cell, content)
            block_holder.add_resource(resource)

        for cell_name, resource in block_holder.resources.items():
            if cell_name not in types_blobs:
                if resource.content is not None:
                    processor_changes.delete(resource.name)
                block_holder.delete_resource(cell_name)
        self.hive_holder.hive.update(processor_changes)


def obtain_types_blobs(files, normalize):
    """files: dict{BlockCellName: Item (str or bytes loaded from file)}
    normalize: Boolean, normalize Blobs (crlf) or not
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
    apply_types(tree, TypeFilter(), result, normalize)
    return result


def apply_types(base_tree, current_types, result, normalize):
    '''
    Params:
        base_tree: {block_name: (CellName, content_str)}
        current_types: TypeFilter
        normalize: Boolean, normalize Blobs (crlf) or not
        result: dict
    '''
    types_resource = base_tree.get('types.bii')
    if types_resource:
        types_filter = TypeFilter.loads(types_resource[1])
        current_types = current_types + types_filter
    for value in base_tree.itervalues():
        if isinstance(value, dict):
            base_tree = value
            apply_types(base_tree, current_types, result, normalize)
        else:
            block_cell_name, filecontent = value
            bii_type = _get_type_cell(filecontent, current_types, block_cell_name)
            blob = Blob(filecontent, is_binary=bii_type.is_binary(), normalize=normalize)
            result[block_cell_name] = bii_type, blob


def _get_type_cell(filecontent, type_filter, cell_name):
    from biicode.common.model.bii_type import UNKNOWN
    bii_type = type_filter.type(cell_name)
    if bii_type == UNKNOWN:
        bii_type = bii_type.from_content(filecontent)
    return bii_type
