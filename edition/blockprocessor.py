from biicode.common.edition.processors.cpp_implementation import CPPImplementationsProcessor
from biicode.common.edition.processors.dep_processor import DependenciesProcessor
from biicode.common.edition.processors.deps_configuration import DependenciesConfigurationProcessor
from biicode.common.edition.processors.main_config_processor import MainConfigProcessor
from biicode.common.edition.processors.virtual_processor import VirtualConfigurationProcessor
from biicode.common.utils.bii_logging import logger
from biicode.common.edition.processors.parse_processor import ParseProcessor
from biicode.common.edition.processors.arduino_entry_points import ArduinoEntryPointProcesor


class BlockProcessor(object):

    def __init__(self, active_langs):
        self.processors = [ParseProcessor(),
                           VirtualConfigurationProcessor()]

        self.processors.append(DependenciesProcessor())
        self.processors.append(CPPImplementationsProcessor())  # The order is important
        self.processors.append(DependenciesConfigurationProcessor())
        if 'arduino' in active_langs:
            self.processors.append(ArduinoEntryPointProcesor())
        # This should be the last one to process mains as it can disable entry points
        self.processors.append(MainConfigProcessor())

    def process(self, block_holder, biiout):
        for p in self.processors:
            logger.debug('Applying processor  %s' % p.__class__.__name__)
            p.do_process(block_holder, biiout)
