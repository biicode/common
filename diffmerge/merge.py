from biicode.common.exception import BiiException
from biicode.common.diffmerge.compare import compare
from copy import copy
from abc import ABCMeta, abstractmethod


class SetThreeWayMerge(object):
    """Generic ThreeWayMerge for set of elements.
    Each set of elements must be a dict beeing the key an element identifier and
    value the value to merge

    merge_elements method is not implemented and will be called with each resource
    that needs a merge"""

    __metaclass__ = ABCMeta

    def __init__(self, base_name, other_name, biiout):
        self.base_name = base_name
        self.other_name = other_name
        self._biiout = biiout

    @abstractmethod
    def merge_elements(self, common, el1, el2):
        """Must return a tuple with:
          1. the merge of el1 and el2
          2. If there was a conflict in merge"""
        raise NotImplementedError()

    def merge(self, base, other, common, base_renames=None, other_renames=None):
        '''
        Merges two blocks
        Params:
            base: dict { name: value }
            other: dict { name: value }
            common: dict { name: value }
            base_renames: Renames object
            other_renames: Renames object
        Returns:
            Dict CellName => Resource with merged contents
        '''
        if not base_renames:
            base_renames = {}

        if not other_renames:
            other_renames = {}

        base_changes = compare(common, base)
        other_changes = compare(common, other)
        base_changes.renames = base_renames
        other_changes.renames = other_renames
        ret = copy(common)

        self._handle_deletion(base_changes, other_changes, ret)
        self._handle_deletion(other_changes, base_changes, ret)
        self._handle_creation(base_changes, other_changes, ret)
        self._handle_creation(other_changes, base_changes, ret)
        self._handle_modify(base_changes, other_changes, ret)
        self._handle_modify(other_changes, base_changes, ret)

        self._handle_renames(base_changes, other_changes, ret)
        self._handle_renames(other_changes, base_changes, ret)

        assert not base_changes.deleted, base_changes.deleted
        assert not base_changes.created, base_changes.created
        assert not base_changes.modified, base_changes.modified
        assert not base_changes.renames, base_changes.renames

        assert not other_changes.deleted, other_changes.deleted
        assert not other_changes.created, other_changes.created
        assert not other_changes.modified, other_changes.modified
        assert not other_changes.renames, other_changes.renames

        return ret

    def _handle_deletion(self, base, other, ret):
        '''handle pure deletions, not including own renames'''
        for k_deleted in base.deleted.keys():
            if k_deleted not in base.renames:
                if k_deleted in other.deleted:  # Both deleted
                    if k_deleted in other.renames:
                        new_name = other.renames[k_deleted]
                        new_other_res = other.created[new_name]
                        old_res = base.deleted[k_deleted]
                        if new_other_res != old_res:
                            self._biiout.warn('%s: CONFLICT (deleted/renamed-modified): '
                                              'Deleted in %s and renamed-modified in %s'
                                              % (new_name, self.base_name, self.other_name))
                            ret[new_name] = other.created[new_name]
                        other.renames.pop(k_deleted, None)
                        other.created.pop(new_name, None)
                    ret.pop(k_deleted, None)
                    other.deleted.pop(k_deleted, None)
                #Deleted in base and modified in other
                elif k_deleted in other.modified:
                    self._biiout.warn('%s: CONFLICT (deleted/modified): '
                                     'Deleted in %s and modified in %s'
                                     % (k_deleted, self.base_name, self.other_name))
                    ret[k_deleted] = other.modified[k_deleted].new
                    other.modified.pop(k_deleted, None)
                elif k_deleted in other.created:
                    raise BiiException("How can it be possible???")
                #Deleted in base and not changed in other, we deleted it
                else:
                    ret.pop(k_deleted, None)
                base.deleted.pop(k_deleted, None)

    def _handle_creation(self, base, other, ret):
        '''handle pure creation in base, not including renames in base'''
        common = {}
        for k_created in base.created.keys():
            base_created = base.created[k_created]
            if k_created not in base.renames.values():
                #Created in both sets
                if k_created in other.created:  # Created Both, compare contents
                    other_created = other.created[k_created]
                    if k_created in other.renames.values():
                        old_name = other.renames.keys()[other.renames.values().index(k_created)]
                        if base_created != other_created:  # Not the same
                            m, conflict = self.merge_elements(common[old_name],
                                                    base_created, other_created)
                            if conflict:
                                self._biiout.warn('%s: CONFLICT (created/renamed): '
                                                  'Created in %s and renamed in %s'
                                                  % (k_created, self.base_name, self.other_name))
                            else:
                                self._biiout.warn('Merged: %s' % k_created)
                            ret[k_created] = m
                        else:  # Same file created in both versions
                            ret[k_created] = base_created
                        other.renames.pop(old_name, None)
                        other.deleted.pop(old_name, None)
                    else:
                        if base_created != other_created:  # Not the same
                            m, conflict = self.merge_elements(None, base_created, other_created)
                            if conflict:
                                self._biiout.warn('%s: CONFLICT (created/created): '
                                                  'Created in %s and created in %s'
                                                  % (k_created, self.base_name, self.other_name))
                            else:
                                self._biiout.warn('Merged: %s' % k_created)
                            ret[k_created] = m
                        else:  # Same file created in both versions
                            ret[k_created] = base_created
                    other.created.pop(k_created, None)
                # If item doesnt exists in previous version cant be other thing that new or none
                elif k_created in other.modified or k_created in other.deleted:
                    raise BiiException("How can it be possible???")
                else:  # FF
                    ret[k_created] = base.created[k_created]
                base.created.pop(k_created, None)

    def _both_modified(self, k_modified, base_modified, other_modified, ret):
        # Modified are a tuple of (old, new)
        modified_other = other_modified[k_modified].new
        modified_base = base_modified[k_modified].new
        old = base_modified[k_modified].old
        if modified_other != modified_base:
            m, conflict = self.merge_elements(old, modified_base, modified_other)
            if conflict:
                self._biiout.warn('%s: CONFLICT (modified/modified): '
                                  'Changed in %s and changed in %s'
                                  % (k_modified, self.base_name, self.other_name))
            else:
                self._biiout.warn('Merged: %s' % k_modified)
        else:
            m = modified_base
        ret[k_modified] = m
        other_modified.pop(k_modified, None)

    def _handle_modify(self, base, other, ret):
        '''
        Params:
            base_resources: Mutable
            other_resources: Mutable
        '''
        #Modified items in base_resources
        for k_modified in base.modified.keys():
            modified = base.modified[k_modified].new
            if k_modified in other.renames:
                new_name = other.renames[k_modified]
                new_res = other.created[new_name]
                old_res = other.deleted[k_modified]
                if old_res != new_res:
                    m, conflict = self.merge_elements(old_res, modified, new_res)
                    if conflict:
                        self._biiout.warn('%s: CONFLICT (changed/renamed): '
                                          'Changed in %s and renamed in %s'
                                          % (new_name, self.base_name, self.other_name))
                    else:
                        self._biiout.warn('Merged: %s' % new_name)
                    ret[new_name] = m
                else:
                    ret[new_name] = modified
                ret.pop(k_modified, None)
                other.renames.pop(k_modified, None)
                other.deleted.pop(k_modified, None)
                other.created.pop(new_name, None)
            else:
                if k_modified in other.modified:  # Both modified, compare contents
                    self._both_modified(k_modified, base.modified, other.modified, ret)
                elif k_modified in other.created or k_modified in other.deleted:
                    # it exists in common_resources, cant be new in other_resources
                    raise BiiException("How can it be possible???")
                else:
                    ret[k_modified] = base.modified[k_modified].new
            base.modified.pop(k_modified, None)

    def _old_rename(self, base, other, old_name, new_name, ret):
        other_new_name = other.renames[old_name]
        old_content = base.deleted[old_name]
        content_other = other.created[other_new_name]
        content_base = base.created[new_name]

        if content_base != content_other:
            if content_base == old_content:
                ret[new_name] = content_other  # FF
            elif content_other == old_content:
                ret[new_name] = content_base  # FF
            else:
                m, conflict = self.merge_elements(old_content, content_base, content_other)
                if conflict:
                    self._biiout.warn('%s: CONFLICT (rename-changed/rename-changed): '
                                      'Changed in %s and changed in %s'
                                      % (new_name, self.base_name, self.other_name))
                else:
                    self._biiout.warn('Merged: %s' % new_name)
                ret[new_name] = m
        else:
            ret[new_name] = content_other

        ret.pop(old_name, None)
        base.deleted.pop(old_name, None)
        base.created.pop(new_name, None)
        base.renames.pop(old_name, None)
        other.renames.pop(old_name, None)
        other.deleted.pop(old_name, None)
        other.created.pop(other_new_name, None)

    def _new_rename(self, base, other, old_name, new_name, ret):
        other_old_name = other.renames.keys()[other.renames.values().index(new_name)]
        other_new_content = other.created[new_name]
        base_new_content = base.created[new_name]
        old_content = base.deleted[old_name]
        other_old_content = other.deleted[other_old_name]

        if other_new_content != base_new_content:
            if base_new_content == old_content and other_new_content != other_old_content:
                ret[new_name] = other_new_content  # FF
            elif other_new_content == other_old_content and base_new_content != old_content:
                ret[new_name] = base_new_content  # FF
            else:
                m, conflict = self.merge_elements(None, base_new_content, other_new_content)
                if conflict:
                    self._biiout.warn('%s: CONFLICT (rename-changed/rename-changed): '
                                      'Changed in %s and changed in %s'
                                      % (new_name, self.base_name, self.other_name))
                else:
                    self._biiout.warn('Merged: %s' % new_name)
                ret[new_name] = m
        else:
            ret[new_name] = other_new_content

        ret.pop(old_name, None)
        ret.pop(other_old_name, None)
        base.deleted.pop(old_name, None)
        base.created.pop(new_name, None)
        base.renames.pop(old_name, None)
        other.renames.pop(other_old_name, None)
        other.deleted.pop(other_old_name, None)
        other.created.pop(new_name, None)

    def _handle_renames(self, base, other, ret):
        '''the renames of base always win here'''
        for old_name, new_name in base.renames.items():
            #old name deleted in other_resources, we delete old and create new
            if old_name in other.renames:
                self._old_rename(base, other, old_name, new_name, ret)
            elif new_name in other.renames.values():
                self._new_rename(base, other, old_name, new_name, ret)
            else:  # not in other renames
                raise BiiException('Merge internal error')
