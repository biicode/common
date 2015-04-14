from biicode.common.exception import BiiException
from biicode.common.model.brl.block_cell_name import BlockCellName
import os
from biicode.common.utils.bii_logging import logger
from biicode.common.model.declare.declaration import Declaration
from biicode.common.model.brl.system_cell_name import SystemCellName


class FortranDeclaration(Declaration):

    def match(self, block_cell_names, origin_block_cell_name=None, paths=None):
        #Try absolute
        try:
            brl = BlockCellName(self.name)
            if brl in block_cell_names:
                return set([brl])
        except:
            pass

        #Try relative
        try:
            name = os.path.normpath(os.path.join(os.path.dirname(origin_block_cell_name),
                                                 self.name))
            brl = BlockCellName(name)
            if brl in block_cell_names:
                return set([brl])
        except:
            pass

        # Try APPROXIMATE, only in same block
        if origin_block_cell_name:
            try:
                block_name = origin_block_cell_name.block_name
                normalized_include = self.normalizedName
                result = set()
                for name in block_cell_names:
                    if name.block_name == block_name:  # Approximate only find in same Block
                        if name.endswith(normalized_include):
                            tail = os.path.split(name)[1]
                            if len(normalized_include) >= len(tail):
                                result.add(name)

                if len(result) == 1:
                    return result

                #TODO: Inform user of multiple matchs
                logger.info("Matchs for name %s are %s" % (self.name, result))
            except Exception as e:
                logger.error("Approximate find failed %s" % str(e))
                pass

        return set()

    def match_system(self, system_cell_names):
        name = SystemCellName(self.name)
        if name in system_cell_names:
            return set([name])
        return set()

    def block(self):
        try:
            return BlockCellName(self.name).block_name
        except:
            return None

    def normalize(self, targets):
        if len(targets) != 1:
            raise BiiException("Incorrect input parameter %s" % targets)
        block_cell_name = iter(targets).next()
        if block_cell_name != self.name:
            return FortranDeclaration(block_cell_name)

    @property
    def normalizedName(self):
        return self.name.lower().replace('\\', '/')
