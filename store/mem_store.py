import copy
from biicode.common.exception import (BiiStoreException, NotInStoreException,
                                      AlreadyInStoreException)


class MemStore(object):
    '''MemStore is the ABC for an in memory store, that could be used
    both for testing (instead of a real DB) or in production for efficiency
    as intermediate caching store, proxying a real store, passed as parameter
    in the constructor. Can be None for testing with in memory only.
    Such store must support the methods invoked, i.e. read(x, 'cell'), the
    underlaying store must have a method called "read_cell(x)".

    The methods called "multi", will append an 's' to the name, and retrieve
    a dict{ID: RequestedObject}

    The store always returns deep copies of objects, to really provide isolation
    and avoid by-reference modifications, when used as a final (non-proxying) store

    Names passed as parameters MUST be the names of the supporting dicts to hold data
    '''

    def __init__(self, store=None):
        self._store = store
        self._init_holders()

    def _get_item(self, item):
        """ this method differentiates if the store is being used in testing or not. If in
        production, it will be a proxy of self._store, and then it does not require to deepcopy
        objects. For testing it is better to ensure things are copied so, no referencial problemas
        are hidden
        """
        if self._store:
            return item
        else:
            return copy.deepcopy(item)

    def _init_holders(self):
        '''derived classes must implement this method, declaring collections
        to be cached, i.e. self.user = {}. Collections in SINGULAR'''
        raise NotImplementedError('Derived class must implement this')

    def read(self, ID, name):
        collection = getattr(self, name)
        try:
            return self._get_item(collection[ID])
        except KeyError:
            if self._store:
                read_method = getattr(self._store, 'read_' + name)
                item = read_method(ID)
                collection[ID] = item
                return item
            else:
                raise NotInStoreException('ID (%s) not found' % str(ID))

    def read_multi(self, IDs, name):
        '''returns a dict {ID: object}'''
        result = {}
        missing = set()
        collection = getattr(self, name)
        for ID in IDs:
            try:
                result[ID] = self._get_item(collection[ID])
            except KeyError:
                missing.add(ID)
        if missing:
            if self._store:
                read_method = getattr(self._store, 'read_%ss' % name)
                items = read_method(missing)  # assumes that return {ID=>value}
                collection.update(items)
                result.update(items)
            #else:
            #    raise NotInStoreException('IDs (%s) not found' % missing)
        return result

    def create(self, value, name, **kwargs):
        '''create has an extra kwargs for extra options, as update_if_current
        '''
        ID = value.ID
        if ID is None:
            raise BiiStoreException('Object without ID %s, %s' % (value, name))
        collection = getattr(self, name)
        if ID in collection:
            raise AlreadyInStoreException('Duplicate key %s in %s' % (ID, name))
        if self._store:
            create_method = getattr(self._store, 'create_' + name)
            create_method(value, **kwargs)
        collection[ID] = self._get_item(value)
        return ID

    def create_multi(self, values, name, **kwargs):
        '''create has an extra kwargs for extra options, as update_if_current
        '''
        collection = getattr(self, name)
        values_dict = {}
        for value in values:
            ID = value.ID
            if ID is None:
                raise BiiStoreException('Object without ID %s, %s' % (value, name))
            if ID in collection:
                raise BiiStoreException('Duplicate key %s in %s' % (ID, name))
            values_dict[ID] = value

        if self._store:
            create_method = getattr(self._store, 'create_%ss' % name)
            create_method(values, **kwargs)
        collection.update(self._get_item(values_dict))

    def update(self, value, name):
        ID = value.ID
        if ID is None:
            raise BiiStoreException('Object without ID %s, %s' % (value, name))
        collection = getattr(self, name)
        if ID not in collection:
            raise BiiStoreException('Non existing ID (%s) in update' % ID)
        if self._store:
            meth = getattr(self._store, 'update_' + name)
            meth(value)
        collection[ID] = self._get_item(value)

    def upsert(self, value, name):
        ID = value.ID
        collection = getattr(self, name)
        if ID is None:
            raise BiiStoreException('Object without ID %s, %s' % (value, name))
        if self._store:
            meth = getattr(self._store, 'upsert_' + name)
            meth(value)
        collection[ID] = self._get_item(value)

    def upsert_multi(self, values, name):
        collection = getattr(self, name)
        values_dict = {}
        for value in values:
            ID = value.ID
            if ID is None:
                raise BiiStoreException('Object without ID %s, %s' % (value, name))
            values_dict[ID] = value

        if self._store:
            create_method = getattr(self._store, 'upsert_%ss' % name)
            create_method(values)
        collection.update(self._get_item(values_dict))

    def delete_multi(self, ids, name):
        '''use with caution :P, only for edition'''
        collection = getattr(self, name)
        if any(ID not in collection for ID in ids):
            raise BiiStoreException('key error in : %s' % name)
        if self._store:
            meth = getattr(self._store, 'delete_%ss' % name)
            meth(ids)
        for ID in ids:
            del collection[ID]

    def delete(self, key, name):
        '''use with caution :P, only for edition'''
        collection = getattr(self, name)
        if key not in collection:
            raise BiiStoreException('key error in : %s' % collection)
        if self._store:
            meth = getattr(self._store, 'delete_%s' % name)
            meth(key)
        del collection[key]

    def update_field(self, name, obj_id, field_name, value):
        # Because:
        # a) field_name is the serial representation of the field
        # b) object must not have a setter for this field
        raise NotImplementedError()
