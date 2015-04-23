from fnmatch import fnmatch


class MainConfigProcessor(object):
    """Class to process mains filters
    """

    def do_process(self, block_holder, biiout):
        #block_name = block_holder.block_name
        mains = block_holder.mains

        for main in mains:
            any_match = False
            for cell, _ in block_holder.simple_resources:
                if fnmatch(cell.name.cell_name,  main.name):
                    cell.hasMain = main.has_main
                    any_match = True
            if not any_match:
                biiout.warn("%s mains: there aren't any matches with %s filter"
                            % (block_holder.block_name, main.name))
