from biicode.common.model.bii_type import CPP
from biicode.common.utils.bii_logging import logger


class ArduinoEntryPointProcesor(object):
    '''
     Processor to detect arduino entry points
     '''
    def do_process(self, block_holder, biiout):
        assert biiout is not None

        for cell, content in block_holder.simple_resources:
            if cell.type == CPP:
                if self.has_setup_and_loop(content.parser):
                    if not cell.hasMain:
                        cell.hasMain = True

    @staticmethod
    def has_setup_and_loop(parser):
        loop = setup = False
        for definition in parser.definitions:
            if definition.name == 'loop' and not definition.scope:
                logger.debug('loop found')
                loop = True
            if definition.name == 'setup' and not definition.scope:
                setup = True
                logger.debug('setup found')
            if setup and loop:
                return True
        return False
