from biicode.common.edition.block_holder import BIICODE_FILE
from collections import defaultdict, OrderedDict
from biicode.common.model.brl.block_cell_name import BlockCellName
import os
from biicode.common.edition.parsing.file_parser import FileParser
from biicode.common.model.blob import Blob
from biicode.common.model.content import Content
from biicode.common.model.resource import Resource
from biicode.common.model.cells import SimpleCell
from biicode.common.model.bii_type import TEXT, BiiType, CPP
from biicode.common.model.brl.cell_name import CellName


def migrate_bii_config(all_files, biiout):
    """ method used for migrating while 'process', e.g. if I am working on and old
    repo from git
    """
    block_files = defaultdict(dict)
    for f, content in all_files.iteritems():
        bcn = BlockCellName(f)
        block_files[bcn.block_name][bcn.cell_name] = content

    deleted = []
    for block_name, files in block_files.iteritems():
        migration = migrate_block_files(block_name, files, biiout)
        if migration is None:
            continue
        config_text, block_deleted = migration
        deleted.extend(block_name + name for name in block_deleted)
        # ensure the resource is created
        name = block_name + BIICODE_FILE
        all_files[name] = config_text

    for delete in deleted:
        del all_files[delete]

    return deleted


def migrate_block_holder(block_holder, biiout):
    """ Necessary for bii-open, that has a different flow to process
    """
    block_name = block_holder.block_name
    resources = block_holder.resources
    files = {name: resource.content.load.load for name, resource in resources.iteritems()
             if isinstance(resource.cell, SimpleCell)}

    migration = migrate_block_files(block_name, files, biiout)
    if migration is None:
        return
    config_text, block_deleted = migration
    for deleted in block_deleted:
        block_holder.delete_resource(deleted)
    name = block_name + BIICODE_FILE
    new_res = Resource(SimpleCell(name, TEXT), Content(name, load=Blob(config_text),
                                                       created=True))
    block_holder.add_resource(new_res)


def migrate_block_files(block_name, block_files, biiout):
    """ actual migration, takes params
    param block_name: BlockName
    param block_files: {CellName: Blob load}
    param biiout: standar bii output
    """
    old_names = ['requirements', 'parents', 'paths', 'dependencies', 'mains']
    old_names = OrderedDict([(k, k) for k in old_names])
    old_names['parents'] = 'parent'

    old_files = [name for name in old_names if 'bii/%s.bii' % name in block_files]
    if not old_files:
        return

    deleted = []

    if BIICODE_FILE in block_files:
        biiout.warn("The following old configuration files exist in your %s block\n"
                     "%s\nMigrating them to your existing %s file, please check it"
                     % (block_name, ', '.join(old_files), BIICODE_FILE))

    current_config = ["# Biicode configuration file migrated from old config files\n"]
    for file_name, config_name in old_names.iteritems():
        current_config.append("[%s]" % config_name)
        if file_name in old_files:
            config_file = 'bii/%s.bii' % file_name
            biiout.warn("Migrating old %s file to new %s configuration file"
                        % (config_file, BIICODE_FILE))
            content = block_files.pop(config_file)
            deleted.append(config_file)
            for line in content.splitlines():
                current_config.append("\t%s" % line)
        current_config.append("")

    current_config.append('[hooks]\n\n[includes]\n\n[data]')
    # This migrate the old data defined in the bii:// way
    for name, content in block_files.iteritems():
        biitype = BiiType.from_extension(CellName(name).extension)
        if biitype == CPP:
            _, data, _, _, _ = FileParser().parse(content)
            if data:
                data_str = ' '.join(d.name for d in data)
                current_config.append('\t%s + %s' % (name, data_str))

    config_text = '\n'.join(current_config)
    return config_text, deleted


def delete_migration_files(deleted_files, folder):
    for filename in deleted_files:
        filepath = os.path.join(folder, filename)
        os.unlink(filepath)
        try:
            os.removedirs(os.path.dirname(filepath))
        except:
            pass
