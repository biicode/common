from biicode.common.utils.bii_logging import logger


def find(biiapi, hive_holder, response, policy, **find_args):
    """ Looks for dependencies in the server
        Returns:
            find_result
    """
    find_request, local_unresolved = hive_holder.find_request(policy=None)

    # ALL this section is to output the user that some unresolved will not be looked for
    # TODO: Improve this by adding output/response to the computation of FindRequest
    #         instead of here
    if local_unresolved:
        response.warn('There are local unresolved dependencies\n'
                      'They will not be searched in the server\n'
                      'Unresolved: %s' % ', '.join([str(x) for x in local_unresolved]))

    if find_args:
        find_request.modify = find_args.get("modify", False)
        find_request.update = find_args.get("update", False)
        find_request.downgrade = find_args.get("downgrade", False)
        find_request.find = find_args.get("find", False)

    if not find_request:
        response.info('No deps to find on server')
        return None

    find_request.policy = policy
    response.info("Finding missing dependencies in server")
    find_result = biiapi.find(find_request, response)
    return find_result


def update_hive_with_find_result(hive_holder, find_result):
    logger.debug("Applying find result %s" % find_result)
    blocks = hive_holder.blocks
    renames = find_result.update_renames
    for block_holder in hive_holder.block_holders:
        unresolved = set()
        includes = block_holder.includes
        paths_size = len(block_holder.paths)
        for declaration in block_holder.unresolved():
            try:
                new_declaration, _ = declaration.prefix(includes, paths_size)
            except:
                new_declaration = declaration
            decl_block = new_declaration.block()
            if decl_block and decl_block not in blocks:
                unresolved.add(new_declaration)

        for version, dep_dict in find_result.resolved.iteritems():
            for unr in unresolved:
                if unr in dep_dict:
                    block_holder.requirements.add_version(version)

        for version, dep_dict in find_result.updated.iteritems():
            external = block_holder.external_targets()
            # TODO: Factorize this pattern, it is becoming repetitive
            external_blocks = {e.block_name for e in external if e.block_name not in blocks}
            if version.block.block_name in external_blocks:
                block_holder.requirements.add_version(version)
            if renames:
                for r in block_holder.simple_resources:
                    cell = r.cell
                    if cell.dependencies.update_resolved(dep_dict, renames):
                        for old, new in renames.iteritems():
                            r.content.update_content_declaration(old, new)

    for block_holder in hive_holder.block_holders:
        block_holder.commit_config()
