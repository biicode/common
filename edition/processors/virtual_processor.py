from biicode.common.edition.parsing.virtual import virtualparser
from biicode.common.model.cells import VirtualCell, SimpleCell
from biicode.common.model.blob import Blob
from biicode.common.model.content import Content
from biicode.common.utils.bii_logging import logger
from biicode.common.edition.parsing.virtual.virtualparser import VirtualParserException
from biicode.common.model.bii_type import BiiType
from biicode.common.edition.parsing.factory import parser_factory
from biicode.common.model.resource import Resource


class VirtualConfigurationProcessor(object):
    virtual_file = 'bii/virtual.bii'

    def do_process(self, block_holder, biiout):
        assert biiout is not None

        self.block_holder = block_holder
        block_name = block_holder.block_name
        try:
            virtuals = set()
            realizations = set()
            try:
                virtual_bii = block_holder[self.virtual_file]
                virtual = virtualparser.parseFile(virtual_bii.content.load.bytes)
                self._process_virtual_config(block_name, virtual, virtuals, realizations, biiout)
            except KeyError:
                logger.debug('No virtual config in %s' % block_name)

            self._virtual_to_simple(virtuals, realizations, biiout)

        except VirtualParserException as e:
            raise VirtualParserException('Error while parsing virtual file %s: %s'
                                         % (block_name, str(e)))

    def _process_virtual_config(self, block_name, virtual, virtuals, realizations, biiout):
        '''Params:
            block_name : BlockName
            virtual: dictionary
        '''

        for virtual_parse_result in virtual.itervalues():
            for cell_name in virtual_parse_result.apply:
                block_cell_name = block_name + cell_name
                try:
                    old_cell = self.block_holder[cell_name].cell
                except KeyError:
                    old_cell = None

                #Build a new virtual cell with the new data, keeping old if existing
                new_cell = VirtualCell(block_cell_name, virtual_parse_result.code,
                                       virtual_parse_result.leaves)
                if old_cell is None:
                    new_cell.type = BiiType.from_extension(block_cell_name.extension)
                else:
                    new_cell.type = old_cell.type

                virtual_resource = Resource(new_cell, None)
                self.block_holder.add_resource(virtual_resource)
                self._process_leaves(new_cell, realizations, biiout)
                virtuals.add(block_cell_name)

    def _virtual_to_simple(self, virtuals, leaves, biiout):
        '''This method checks for those cells that were virtual or realization, but not anymore,
        maybe because the virtual.bii file does not exist, or maybe it doesn't refer to them
        @param virtual: a set of block cell names of those that have been processed as virtual
        @param realizations: as set of BlockCellName of those cells processed as realizations
        @param biiout: biiout
        '''
        for cell, _ in self.block_holder.resources.values():
            if isinstance(cell, VirtualCell):
                if cell.name not in virtuals:
                    biiout.warn('File %s is not virtual anymore' % cell.name)
                    self.block_holder.delete_resource(cell.name.cell_name)
                    self.processor_changes.delete(cell.name)
            else:
                if cell.container and cell.name not in leaves:
                    cell.container = None

    def _process_leaves(self, virtual_cell, realizations, biiout):
        '''for a virtual cell, creates the leaves if they don't exist
        @param virtual_cell: the cell that serves as base
        @param realizations: a set to add the leaves BlockCellNames
        @param biiout: biiout
        '''
        block_cell_name = virtual_cell.name
        for leave in virtual_cell.resource_leaves:
            realizations.add(leave)
            try:
                cell = self.block_holder[leave.cell_name].cell
            except KeyError:
                #The leave it is pointing does not exist
                biiout.info('%s virtual realization not existing, creating it' % leave)
                cell = SimpleCell(leave)
                cell.type = virtual_cell.type
                content = Content(leave, Blob(""), created=True)
                content.parser = parser_factory(cell.type, cell.name.cell_name)
                self.block_holder.add_resource(Resource(cell, content))
            cell.container = block_cell_name
