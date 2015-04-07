from biicode.common.model.content import Content


class ProcessorChanges(object):
    def __init__(self):
        self._delete = set()
        self._upsert = {}
        self._blobs_changed = set()

    def __nonzero__(self):
        return len(self._delete) + len(self._upsert) > 0

    @property
    def deleted(self):
        return self._delete

    @property
    def blobs_changed(self):
        return self._blobs_changed

    @property
    def upserted(self):
        return self._upsert

    def upsert(self, block_cell_name, content, blob_changed=False):
        '''
        Params:
            block_cell_name: Modified content
            content: New content
        '''
        assert isinstance(content, Content)
        assert isinstance(blob_changed, bool)
        self._delete.discard(block_cell_name)
        self._upsert[block_cell_name] = content
        if blob_changed:
            self._blobs_changed.add(block_cell_name)

    def delete(self, block_cell_name):
        try:
            del self._upsert[block_cell_name]
        except KeyError:
            pass
        self._delete.add(block_cell_name)
