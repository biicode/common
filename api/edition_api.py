from abc import ABCMeta, abstractmethod
from biicode.common.model.cells import SimpleCell
from biicode.common.edition.hive_holder import HiveHolder


class EditionAPI(object):
    '''This API is basically a CRUD over the hive objects, it is for ONE
    hive only, cells are referenced with their BlockCellName'''
    __metaclass__ = ABCMeta

    @abstractmethod
    def read_edition_contents(self, block_cell_names):
        raise NotImplementedError()

    @abstractmethod
    def upsert_hive(self, hive):
        raise NotImplementedError()

    @abstractmethod
    def upsert_edition_contents(self, content):
        raise NotImplementedError()

    @abstractmethod
    def delete_edition_contents(self, block_cell_name):
        raise NotImplementedError()

    @abstractmethod
    def read_hive(self):
        raise NotImplementedError()

    def get_holder(self, hive=None):
        if hive is None:
            hive = self.read_hive()

        simple_cells_names = hive.cells
        contents = self.read_edition_contents(simple_cells_names) if simple_cells_names else {}
        # creation of cells
        cells = {name: SimpleCell(name) for name in simple_cells_names}
        assert len(contents) == len(simple_cells_names)
        hive_holder = HiveHolder(hive, cells, contents)
        return hive_holder

    def save_hive_changes(self, hive, processor_changes):
        self.upsert_hive(hive)  # The hive is always updated

        if not processor_changes:
            return

        self.upsert_edition_contents(processor_changes.upserted.values())
        self.delete_edition_contents(processor_changes.deleted)
