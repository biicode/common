

class ParseProcessor(object):

    def do_process(self, block_holder, biiout):
        for resource in block_holder.simple_resources:
            resource.parse(biiout)
