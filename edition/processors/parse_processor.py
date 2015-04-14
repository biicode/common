

class ParseProcessor(object):

    def do_process(self, block_holder, changes, biiout):
        for resource in block_holder.simple_resources:
            if resource.parse(biiout):
                changes.upsert(resource.name, resource.content)
