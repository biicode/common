from biicode.common.edition.blockprocessor import BlockProcessor
from biicode.common.utils.bii_logging import logger
from biicode.common.edition import changevalidator
from collections import defaultdict
from biicode.common.model.symbolic.reference import References
from biicode.common.exception import BiiException, NotFoundException
from biicode.common.deps.block_version_graph import BlockVersionGraph
from biicode.common.deps.closure_builder import build_closure
from biicode.common.model.symbolic.block_version_table import BlockVersionTable
from biicode.common.edition.project_dependencies import ProjectDependencies


def blocks_process(hive_holder, biiout):
    """ This function processes the edition blocks of the hive, nothing related with deps.
    It searches resolved-unresolved between edition blocks.
    param hive_holder: current ProjectHolder
    param processor_changes: ProcessorChanges to annotate changes done during process
    param biiout: biiout
    """

    logger.debug("---------- process blocks --------")

    settings = hive_holder.settings
    langs = [lang for lang in ['arduino', 'fortran', 'python']
             if getattr(settings, lang, None)]
    block_processor = BlockProcessor(langs)
    for block_holder in hive_holder.block_holders:
        changevalidator.check_block_size(block_holder, biiout)
        block_processor.process(block_holder, biiout)


def deps_process(biiapi, hive_holder, biiout, settings=None):
    """Try to find unresolved in the existing external references or in the external references
    of the previous execution, so moving a file from one place to another does not require a
    find
    """
    logger.debug("---------- process deps --------")
    _change_local_versions(hive_holder)  # to edition ones if you opened blocks
    _discover_tag_versions(hive_holder, biiapi, biiout)
    common_table = compute_common_table(hive_holder)  # BlockVersionTable
    _update_resolved(biiapi, hive_holder, common_table, biiout)

    src_graph, references = compute_src_graph(hive_holder, common_table)
    dep_graph, closure, overwrites = build_closure(biiapi, references, common_table, settings,
                                                   biiout)
    hive_dependencies = ProjectDependencies()
    hive_dependencies.src_graph = src_graph  # BlockVersionGraph
    hive_dependencies.dep_graph = dep_graph  # BlockVersionGraph
    hive_dependencies.closure = closure
    hive_dependencies.references = references
    hive_holder.hive_dependencies = hive_dependencies

    real_graph = src_graph + dep_graph
    real_graph.sanitize(biiout)
    _update_requirements(hive_holder, real_graph, overwrites, common_table, biiout)

    for block_holder in hive_holder.block_holders:
        block_holder.commit_config()  # Resource


def _change_local_versions(hive_holder):
    '''
    If we are now editing a block that before was an external dependency (it was in the dep table)
    then version is changed to the edition one (version = None)
    '''
    edition_versions = hive_holder.versions
    for block_holder in hive_holder.block_holders:
        for block_name in block_holder.requirements:
            hive_version = edition_versions.get(block_name)
            if hive_version:
                block_holder.requirements.add_version(hive_version)


def _discover_tag_versions(hive_holder, biiapi, out):
    '''
    If a version is specify with a tag instead of a time we must discover corresponding time
    '''
    for block_holder in hive_holder.block_holders:
        for name, version in block_holder.requirements.iteritems():
            if version.tag is not None:
                try:
                    if version.time is None:  # Discover last matching time for given version
                        full_version = biiapi.get_version_by_tag(version.block, version.tag)
                        block_holder.requirements[name] = full_version
                        block_holder.commit_config()
                    else:  # Check that time and tag match
                        delta = biiapi.get_version_delta_info(version)
                        if delta.versiontag != version.tag:
                            out.error('Tag and version do not match in %s. '
                                  'Tag will be ignored' % version.to_pretty())
                except NotFoundException as e:
                    out.error("%s/biicode.conf: %s" % (block_holder.block_name, str(e)))


def compute_common_table(hive_holder):
    ''' Computes a common dependencies table for all opened blocks in this hive. This table is
    used as the main input to compute the closure of dependencies. Two opened blocks MUST have
    the same version-dependency of the same block, if one has A: 1, the other cannot have A: 2,
    this is changed and an exception can be raised to point out this incompatibility
    Return:
        BlockVersionTable
    '''
    result_table = hive_holder.versions
    parents = {b.block_name: b.parent for b in hive_holder.block_holders}
    for block_holder in hive_holder.block_holders:
        for new_name, new_version in block_holder.requirements.iteritems():
            if new_name not in parents:
                try:
                    old_version = result_table[new_name]
                    if new_version != old_version:
                        raise BiiException('Incompatible requirement in "%s": "%s"\n'
                                           'Conflicts with version "%s"'
                                           % (block_holder.block_name, new_version, old_version))
                except KeyError:
                    result_table[new_name] = new_version
    return result_table


def _handle_block_deps(block_holder, directer):
    """ for a given edition BlockHolder, check if its external dependencies are resolved in
    any of the blocks indicated by the requirements (all together via common_table)
    """
    includes = block_holder.includes
    paths_size = len(block_holder.paths)
    for resource in block_holder.simple_resources:
        cell = resource.cell
        for declaration in cell.dependencies.unresolved.copy():
            try:
                # declaration contains block name prefix
                block_name = declaration.block()
                block_cell_names = directer[block_name]
                include_path = None
                new_declaration = declaration
            except KeyError:  # declaration do not contain block name prefix
                try:
                    new_declaration, include_path = declaration.prefix(includes, paths_size)
                    block_name = new_declaration.block()
                    block_cell_names = directer[block_name]
                except:
                    continue

            targets = new_declaration.match(block_cell_names)
            if targets:
                # TODO? new_targets = block_holder.translate_virtuals(targets)
                cell.dependencies.add_path(include_path)
                cell.dependencies.resolve(declaration, targets)


def _update_resolved(biiapi, hive_holder, common_table, biiout):
    """ in block_process, the dependencies inside blocks are managed. This method handles the
    discovery and removal of dependencies between different blocks, both simultaneously
    edited blocks, but also between published blocks living in Deps
    """
    directer = {}
    for block_holder in hive_holder.block_holders:
        directer[block_holder.block_name] = block_holder.block_cell_names

    blocks = hive_holder.blocks
    for block_name, version in common_table.iteritems():
        if block_name not in blocks and version.time is not None and version.time != -1:
            # If time is None it means is in edition. Either it is unused and will be removed
            # later in update_requirements or its an error (the user manually wrote it in the
            # requirements file or deleted the block without closing it).
            # Here we could attempt to retrieve last published version but we agreed the user
            # should use close command and we wont fix manual removals.
            try:
                cell_names = biiapi.get_cells_snapshot(version)
                directer[block_name] = set([block_name + c for c in cell_names])
            except BiiException as e:
                biiout.error("Unable to get files from %s\n%s" % (version.to_pretty(), str(e)))

    for block_holder in hive_holder.block_holders:
        _handle_block_deps(block_holder, directer)


def compute_src_graph(hive_holder, common_table):
    """ computes just the src part of the full version graph.
    Side effect: updates requirements of blocks to actually point to real dep versions
    """
    graph = BlockVersionGraph()
    versions = hive_holder.versions
    graph.add_nodes(versions.itervalues())
    references = References()
    for block_holder in hive_holder.block_holders:
        dep_table = block_holder.requirements
        base_version = versions[block_holder.block_name]
        for target_bcn in block_holder.external_targets():
            target_block_name = target_bcn.block_name
            if target_block_name in versions:
                other_version = versions[target_block_name]
            else:
                other_version = common_table[target_block_name]
                references[other_version].add(target_bcn.cell_name)
            graph.add_edge(base_version, other_version)
            dep_table.add_version(other_version)
    return graph, references


def _update_requirements(hive_holder, real_graph, overwrites, common_table, response):
    """ After all deps processing, the requirements of each edited block needs to be updated.
    Unused versions can be removed, but also versions might be added, as they are actually
    necessary to define the current dependency graph of a given edited block
    """
    versions = hive_holder.versions
    for block_holder in hive_holder.block_holders:
        # First compute a new version of the requirements, which is a partial version of common
        new_table = common_table.copy()

        current_version = versions[block_holder.block_name]
        neighbours = real_graph.neighbours(current_version)
        neighbours_table = BlockVersionTable(neighbours)
        assert len(neighbours) == len(neighbours_table)  # Neighbors cant be different versions
        closure = real_graph.compute_closure(current_version)
        closure_versions = defaultdict(set)
        for version in closure:
            closure_versions[version.block_name].add(version)

        for block_name, version in new_table.items():
            if block_name not in closure_versions:
                new_table.pop(block_name)
            elif block_name not in neighbours_table:
                delete = True
                for over_base, over_versions in overwrites.iteritems():
                    if over_base in closure and version in over_versions:
                        delete = False
                        break
                if delete:
                    new_table.pop(block_name)
            else:
                assert version == neighbours_table[block_name]
                pass

        # Update the table, and inform the user of any automatic changes done
        for block_name, version in new_table.iteritems():
            if version.time is None:
                version = hive_holder[block_name].parent
                assert version.time is not None
                new_table.add_version(version)

        dep_table = block_holder.requirements
        if new_table != dep_table:
            # Inform about added references
            for block_name, version in new_table.iteritems():
                if block_name not in dep_table:
                    response.warn('Adding to %s "requirements" version %s'
                                  % (block_holder.block_name, str(version)))
            #inform about deleted references
            for block_name, version in dep_table.iteritems():
                if block_name not in new_table:
                    response.warn('Unused reference to "%s" from %s [requirements]'
                                  % (str(version), block_holder.block_name))
                    if version.time is not None:
                        new_table.add_version(version)
            block_holder.requirements = new_table
