'''
Common helper functions for processors tests
'''
from biicode.common.output_stream import OutputStream


def process_holder(holder, processor):
    """This function performs common operation in processor test:
        - Process holder
        @return changes.result_changes and process response
    """

    biiout = OutputStream()
    processor.do_process(holder, biiout)
    return biiout
