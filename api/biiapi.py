from abc import ABCMeta, abstractmethod
from biicode.common.model.symbolic.reference import References
from biicode.common.edition.block_holder import BlockHolder


class BiiAPI(object):
    '''The main interface to user-access biicode published information'''
    #TODO: Clearly specify raised Exceptions in each method
    #TODO: Validate implementations, to check that they really follow this specification
    __metaclass__ = ABCMeta

    def require_auth(self):
        """Require a logged username"""
        raise NotImplementedError()

    @abstractmethod
    def get_dep_table(self, block_version):
        """
        return: BlockVersionTable
        """
        raise NotImplementedError()

    @abstractmethod
    def get_published_resources(self, references):
        """
        param references: References
        return: ReferencedResources
        """
        raise NotImplementedError()

    @abstractmethod
    def get_cells_snapshot(self, block_version):
        """
        return: [CellName] of the cells corresponding to such block_version
        """
        raise NotImplementedError()

    def get_block_holder(self, block_version):
        """"
        return: BlockHolder
        """
        assert block_version.time is not None
        refs = References()
        block_cells_name = self.get_cells_snapshot(block_version)
        refs[block_version] = set(block_cells_name)
        resources = self.get_published_resources(refs)
        return BlockHolder(block_version.block_name, resources[block_version])

    @abstractmethod
    def get_renames(self, brl_block, t1, t2):
        '''return a Renames object (i.e. a dict{oldName:newName}'''
        raise NotImplementedError()

    @abstractmethod
    def publish(self, publish_request):
        raise NotImplementedError()

    @abstractmethod
    def get_version_delta_info(self, block_version):
        raise NotImplementedError()

    @abstractmethod
    def get_version_by_tag(self, brl_block, version_tag):
        raise NotImplementedError()

    @abstractmethod
    def get_block_info(self, brl_block):
        raise NotImplementedError()

    @abstractmethod
    def find(self, finder_request, response):
        '''Finder and updater
        return a FinderResult'''
        raise NotImplementedError()

    @abstractmethod
    def get_server_info(self):
        ''' Gets the server info ServerInfo object'''
        raise NotImplementedError()

    @abstractmethod
    def authenticate(self):
        ''' Gets the token'''
        raise NotImplementedError()
