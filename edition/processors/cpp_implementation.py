from biicode.common.model.bii_type import BiiType, CPP
import os
from collections import defaultdict
from biicode.common.edition.parsing.code_reference import CPPItem


class CPPImplementationsProcessor(object):
    '''
     processor to detect implementations in C++, a very difficult task, so this processor is not
     perfect.
     '''
    def do_process(self, block_holder, biiout):
        assert biiout is not None
        # ALL definitions are stored in a dict for easy checking
        #For functions and vars # {blockName: scope: name: set(BlockCellName)}

        simple_resources = [r for r in block_holder.simple_resources
                            if r.cell.type == CPP]
        simple_names = defaultdict(set)
        defs_dict = self._set_default_definitions(simple_resources, simple_names)

        # Now we check every cell against the dict of definitions
        for cell, content in simple_resources:
            implicits = set()
            self.check_implementations_by_name(cell, simple_names, implicits)  # file.h => file.cpp
            self.check_declarations(cell, content, defs_dict, implicits)
            implicits = self.resolve_virtuals(block_holder, implicits)
            cell.dependencies.implicit = implicits

    def _set_default_definitions(self, simple_resources, simple_names):
        defs_dict = {}
        for r in simple_resources:
            # ONLY implementation (.c, .cpp) can be implementations
            name = r.cell.name
            if name.extension not in BiiType.cpp_src_exts:
                continue
            simple_names[os.path.splitext(name)[0]].add(name)
            for definition in r.content.parser.definitions:
                assert definition.type == CPPItem.METHOD or definition.type == CPPItem.VAR
                defs_dict.setdefault(name.block_name, {}).\
                          setdefault(definition.scope, {}).\
                          setdefault(definition.name, set()).add(name)
        return defs_dict

    def check_implementations_by_name(self, cell, simple_names, implicits):
        '''Check by name file.h => file.cpp'''
        if cell.name.cell_name.extension not in BiiType.cpp_src_exts:  # HEADER
            sources = simple_names.get(os.path.splitext(cell.name)[0])
            if sources:
                implicits.update(sources)

    def check_declarations(self, cell, content, defs_dict, implicits):
        for declaration in content.parser.declarations:
            try:
                if declaration.type in [CPPItem.CLASS, CPPItem.STRUCT]:
                    scope = CPPItem.extend_scope(declaration.scope, declaration.name)
                    ds = defs_dict[cell.name.block_name][scope].values()
                    for d in ds:
                        d.discard(cell.name)
                        #logger.debug('Adding class/struct as implicit %s because %s in defs dict'
                        #             % (cell.name, str(d)))
                        implicits.update(d)
                else:
                    ds = defs_dict[cell.name.block_name][declaration.scope][declaration.name]
                    ds.discard(cell.name)
                    #logger.debug('Adding implicit %s: %s because %s is in defs dict'
                    #             % (cell.name, str(ds), str(declaration.name)))
                    implicits.update(ds)
            except KeyError:
                # Declaration not found in definitions
                pass

    @staticmethod
    def resolve_virtuals(block_holder, implicits):
        ''''Take into account if implemented by virtual resource'''
        new_implicits = set()
        for implicit in implicits:
            assert implicit.block_name == block_holder.block_name
            cell2 = block_holder[implicit.cell_name].cell
            target = cell2.container or cell2.name
            new_implicits.add(target)
        return new_implicits
