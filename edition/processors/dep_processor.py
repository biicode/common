''' DependenciesProcessor class for finding internal dependencies within a hive
'''
from biicode.common.dev.system_resource_validator import getSystemNameValidatorFor
from biicode.common.model.declare.data_declaration import DataDeclaration
from fnmatch import fnmatch


class DependenciesProcessor(object):
    ''' Processor class for finding internal dependencies within a hive '''

    def do_process(self, block_holder, biiout):
        assert biiout is not None
        #TODO: response some information?
        self.block_holder = block_holder
        self._biiout = biiout
        self._define_datas()
        self._search_system()
        self._handle_deps()

    def _define_datas(self):
        # Use information contained in biicode tags:
        datas = self.block_holder.data
        if not datas:
            return

        block_name = self.block_holder.block_name
        cell_names = self.block_holder.cell_names
        for data in datas:
            dependents = dependents = {c for c in cell_names if fnmatch(c, data.pattern)}
            if not dependents:
                self._biiout.warn('In %s, definition %s\n\t'
                                  'There are no files matching pattern %s'
                                  % (block_name, data, data.pattern))
                continue

            for dependent in dependents:
                cell = self.block_holder[dependent].cell
                for dep in data.dependencies:
                    cell.dependencies.unresolved.add(DataDeclaration(dep.name))

    def _handle_deps(self):
        '''
        Matches internal block dependencies with block files
        '''
        block_cell_names = self.block_holder.block_cell_names
        paths = self.block_holder.paths
        show_warn_message = True
        for resource in self.block_holder.simple_resources:
            cell = resource.cell
            for declaration in cell.dependencies.unresolved.copy():
                #declaration_block = declaration.block()
                #if not declaration_block or declaration_block == self.block_holder.block_name:
                targets = declaration.match(block_cell_names=block_cell_names,
                                            origin_block_cell_name=cell.name,
                                            paths=paths)
                if targets:
                    if declaration.block() == self.block_holder.block_name:
                        if show_warn_message:
                            show_warn_message = False
                            self._biiout.warn('Block %s has absolute paths, like: #include "%s" '
                                              'within same block not recommended.\nConsider using'
                                              ' relative path or using the [paths] config'
                                              % (self.block_holder.block_name, declaration))
                    new_targets = self.block_holder.translate_virtuals(targets)
                    cell.dependencies.resolve(declaration, new_targets)
                    cell.dependencies.add_path(getattr(declaration, 'path', None))

    def _search_system(self):
        """try to match unresolved declaration to system as stdio.h, math.h"""
        for cell, _ in self.block_holder.simple_resources:
            sys_validator = getSystemNameValidatorFor(cell)
            sys_names = sys_validator.names()
            deps = cell.dependencies
            for declaration in deps.unresolved.copy():
                system_match = declaration.match_system(sys_names)
                if system_match:
                    deps.resolve_system(declaration, system_match)
