from biicode.common.model.cells import SimpleCell
from fnmatch import fnmatch
from biicode.common.model.deps_props import DependenciesProperties
from biicode.common.model.declare.data_declaration import DataDeclaration


class DependenciesConfigurationProcessor(object):
    """Configuration for user defined explicit dependencies

    Processing of [dependencies] file
    """

    def do_process(self, block_holder, biiout):
        self._process_deps(block_holder, biiout)
        self._process_data(block_holder, biiout)

    def _process_deps(self, block_holder, biiout):
        # Use information contained in biicode tags:
        deps = block_holder.dependencies
        if not deps:
            return

        block_name = block_holder.block_name
        cell_names = block_holder.cell_names
        for dep_configuration in deps:
            dependents = {c for c in cell_names if fnmatch(c, dep_configuration.pattern)}
            if not dependents:
                biiout.warn('%s/biicode.conf, [dependencies] %s\n\t'
                              'There are no files matching pattern %s'
                              % (block_name, dep_configuration, dep_configuration.pattern))
                continue
            # Filter unexisting dependency files
            matching_cells = []
            for dep in dep_configuration.dependencies:
                local_match = False
                for cell in cell_names:
                    if fnmatch(cell, dep.name):
                        matching_cells.append(block_name + cell)
                        local_match = True
                if not local_match:
                    biiout.warn('%s/biicode.conf, [dependencies] %s\n\t'
                              'There are no files matching pattern %s'
                              % (block_name, dep_configuration, dep.name))

            for dependent in dependents:
                cell = block_holder[dependent].cell
                if isinstance(cell, SimpleCell):
                    dep_configuration.update_dependencies(cell.dependencies.implicit,
                                                          matching_cells)
                    cell.dependencies.implicit.discard(cell.name)
                    cell.dependencies._force_properties_support()  # FIXME: Calling private

    def _process_data(self, block_holder, biiout):
        # Use information contained in biicode tags:
        deps = block_holder.data
        if not deps:
            return

        block_name = block_holder.block_name
        cell_names = block_holder.cell_names
        for dep_configuration in deps:
            dependents = {c for c in cell_names if fnmatch(c, dep_configuration.pattern)}
            if not dependents:
                biiout.warn('%s/biicode.conf, [data] %s\n\t'
                              'There are no files matching pattern %s'
                              % (block_name, dep_configuration, dep_configuration.pattern))
                continue
            # Filter unexisting dependency files
            matching_cells = set()
            matching_patterns = set()
            for dep in dep_configuration.dependencies:
                local_match = False
                for cell in cell_names:
                    if fnmatch(cell, dep.name):
                        matching_cells.add(block_name + cell)
                        matching_patterns.add(dep.name)
                        local_match = True
                if not local_match:
                    biiout.warn('%s/biicode.conf, [data] %s\n\t'
                              'There are no files matching pattern %s'
                              % (block_name, dep_configuration, dep.name))

            for dependent in dependents:
                cell = block_holder[dependent].cell
                if isinstance(cell, SimpleCell):
                    for matching_cell in matching_cells:
                        cell.dependencies.resolved.add(DataDeclaration(matching_cell))
                        cell.dependencies.explicit.add(matching_cell)
                        cell.dependencies.properties.add_property(matching_cell,
                                                                  DependenciesProperties.DATA)
                    cell.dependencies.explicit.discard(cell.name)
                    for matching_pattern in matching_patterns:
                        cell.dependencies.unresolved.discard(DataDeclaration(matching_pattern))
                    cell.dependencies._force_properties_support()  # FIXME: Calling private
