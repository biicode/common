from abc import ABCMeta, abstractmethod
from biicode.common.model.cells import SimpleCell
from biicode.common.edition.project_holder import ProjectHolder


class EditionAPI(object):
    '''This API is basically a CRUD over the hive objects, it is for ONE
    hive only, cells are referenced with their BlockCellName'''
    __metaclass__ = ABCMeta

    @abstractmethod
    def read_edition_contents(self):
        """ read all contents (without blobs, just the parsing meta-data)
        from project DB
        """
        raise NotImplementedError()

    @abstractmethod
    def upsert_edition_contents(self, contents):
        raise NotImplementedError()

    @abstractmethod
    def delete_edition_contents(self, block_cell_name):
        raise NotImplementedError()

    def get_holder(self):
        contents = self.read_edition_contents()
        # creation of cells
        cells = {name: SimpleCell(name) for name in contents}
        hive_holder = ProjectHolder(cells, contents)
        return hive_holder

    def save_hive_changes(self, hive_holder):
        updated = []
        current = []
        for (_, content) in hive_holder.resources.itervalues():
            if content:
                if content.meta_updated or content.blob_updated:
                    updated.append(content)
                current.append(content.ID)

        self.upsert_edition_contents(updated)

        # TOD: Improve this query, assign responsibility directly to store
        actual_contents = self.read_edition_contents()
        to_delete = set(actual_contents.keys()).difference(current)
        self.delete_edition_contents(to_delete)
