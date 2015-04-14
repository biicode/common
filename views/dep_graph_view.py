

def closure_tree(closure, source_cells, settings=None):
    """Returns the closure as a python dictionary, containing all information"""
    from biicode.common.model.cells import VirtualCell

    result = {}
    # some variables:

    def _update_dep_block_levels(block_name):
        if block_name != "system":
            base_block = result[block_name]
            new_dep_level = base_block["level"] + 1
            for bn in base_block["dep"]:
                bd = result[bn]
                bd["level"] = max(bd["level"], new_dep_level)
                _update_dep_block_levels(bn)

    def _add_block(b_name, is_dep=None, base_level=None):
        """Utility: add a block to the result"""
        _block = result.setdefault(b_name, {"level": 0,
                                            "cells": {},
                                            "dep": {}})
        if is_dep is not None:
            _block["src"] = not is_dep
        if base_level is not None:
            level_before = _block["level"]
            _block["level"] = max(level_before, base_level + 1)
            if level_before != _block["level"]:
                # update dependent blocks levels:
                _update_dep_block_levels(b_name)
        return _block

    def _add_cell_deps(where, deps, _type, base_block_name):
        """Utility: add cell dependencies of type:
            "e" (explicit), "i" (implicit), "s" (system)
        """
        for d in deps:
            if _type == "s":
                _dep_b_name = "system"
                _dep_c_name = str(d)
            elif _type == "u":
                _dep_b_name = "unresolved"
                _dep_c_name = str(d)
            else:
                _dep_b_name = d.block_name
                _dep_c_name = d.cell_name

            if _dep_b_name != base_block_name:
                # block dependencies:
                result[base_block_name]["dep"].setdefault(_dep_b_name, {})
                _add_block(_dep_b_name,
                           is_dep=True if _type in ["s", "u"] else None,
                           base_level=result[base_block_name]["level"])
            # this is the point to add system cells to pseudo-block system:
            if _type == "s":
                result["system"]["cells"].setdefault(_dep_c_name, {"type": "SYS"})
            if _type == "u":
                result["unresolved"]["cells"].setdefault(_dep_c_name, {"type": "UNKNOWN"})
            where.setdefault(_type, []).append([_dep_b_name, _dep_c_name])

    def _add_cell(cell, is_dep=False):
        """Utility: Add a cell to the result"""
        c_name = cell.name
        _b_name = c_name.block_name
        _b = _add_block(_b_name, is_dep)
        _cells = _b["cells"]
        # the cell name acts as key:
        _c = _cells.setdefault(c_name.cell_name, {"dep": {}, "resolved": True})
        _c["is_virtual"] = isinstance(cell, VirtualCell)
        _c["has_main"] = cell.hasMain
        _c["type"] = str(cell.type)
        if _c["is_virtual"]:  # leaves are special case of dependency (virtual)
            leaves = cell.resource_leaves[:]
            if settings:
                current = cell.evaluate(settings)
                # Sorting so virtual realization is in 0 position of the array
                leaves = sorted(leaves, key=(lambda x: 0 if x == current else 1))
            _c["dep"]["v"] = [[l.block_name, l.cell_name] for l in leaves]

        else:
            deps = cell.dependencies
            if deps.explicit:   # BlockCellNames(s)
                _add_cell_deps(_c["dep"], deps.explicit, "e", base_block_name=_b_name)
            if deps.implicit:   # BlockCellNames(s)
                _add_cell_deps(_c["dep"], deps.implicit, "i", base_block_name=_b_name)
            if deps.system:    # SystemResourceName(s)
                _add_cell_deps(_c["dep"], deps.system, "s", base_block_name=_b_name)
            if deps.data:  # BlockCellName(s)
                _add_cell_deps(_c["dep"], deps.data, "d", base_block_name=_b_name)
            if deps.unresolved:
                _add_cell_deps(_c["dep"], deps.unresolved, "u", base_block_name=_b_name)

    # first, the closure cells:
    for _, (resource, _) in closure.iteritems():
        _add_cell(resource.cell, is_dep=True)

    for cell in source_cells:
        _add_cell(cell)

    return result
