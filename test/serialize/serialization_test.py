#!/usr/bin/python
# -*- coding: utf-8 -*-
from biicode.common.utils.serializer import ClassTypedSerializer, Deserializer, serialize
from biicode.common.model.cells import SimpleCell, CellDeserializer, VirtualCell
from biicode.common.model.id import ID, UserID
from biicode.common.model.bii_type import BiiType, SOUND
from biicode.common.model.brl.system_cell_name import SystemCellName
from biicode.common.model.dependency_set import DependencySet
from biicode.common.edition.parsing.cpp.drl_parser import DRLCPPParser
from biicode.common.edition.parsing.parser import Parser
from biicode.common.model.content import ContentDeserializer, Content
from biicode.common.model.blob import Blob
from biicode.common.diffmerge.compare import Changes
from biicode.common.find.finder_result import FinderResult
from biicode.common.find.finder_request import FinderRequest
from biicode.common.model.brl.brl_block import BRLBlock
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.brl.cell_name import CellName
from biicode.common.model.symbolic.block_version_table import BlockVersionTable
from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.model.symbolic.reference import Reference, ReferencedDependencies
from biicode.common.model.renames import Renames
from biicode.common.model.sha import SHA
from biicode.common.model.declare.cpp_declaration import CPPDeclaration
from biicode.common.model.declare.python_declaration import PythonDeclaration
from biicode.common.diffmerge.changes import ChangesDeserializer, Modification
from biicode.common.api.ui import BiiResponse, Message
from biicode.common.test.bii_test_case import BiiTestCase
from biicode.common.output_stream import DEBUG
from biicode.common.find.policy import Policy


class SerializationTest(BiiTestCase):
    '''serialization of objects of model ONLY in common'''

    def test_bii_type(self):
        b1 = BiiType(SOUND)
        s1 = serialize(b1)

        b2 = BiiType.deserialize(s1)
        self.assertEqual(b1, b2)

    def test_declarations(self):
        d1 = CPPDeclaration('path/to/file.h')
        s = d1.serialize()
        d2 = CPPDeclaration.deserialize(s)
        self.assertEqual(d1, d2)

        d1 = PythonDeclaration("import sys")
        s = d1.serialize()
        d2 = PythonDeclaration.deserialize(s)
        self.assertEqual(d1, d2)

    def test_dependency_set(self):
        d1 = DependencySet()
        d1.add_implicit(BlockCellName("user/block/path/file2.h"))
        d1.add_implicit(BlockCellName("user/block/path/file3.h"))
        d1.add_implicit(BlockCellName("user/block/path/file4.h"))
        names = set()
        names.add(CPPDeclaration("iostream.h"))
        d1.update_declarations(names)

        s = d1.serialize()
        d2 = DependencySet.deserialize(s)
        self.assert_bii_equal(d1, d2)

    def test_parsers(self):
        p = DRLCPPParser()
        s = p.serialize()
        p2 = Parser.deserialize(s)
        self.assert_bii_equal(p, p2)

        p = DRLCPPParser()
        s = p.serialize()
        p2 = Parser.deserialize(s)
        self.assert_bii_equal(p, p2)

    def test_content(self):
        #Content with ContentID
        c = Content(ID((0, 1, 2)), load=Blob("Hello"))
        s = c.serialize()
        c2 = ContentDeserializer(ID).deserialize(s)
        self.assertEqual(c, c2)

        #Content with BlockCellName
        c = Content(BlockCellName("user/block/path/to/file.h"), load=Blob("Bye"))
        s = c.serialize()
        c2 = ContentDeserializer(BlockCellName).deserialize(s)
        self.assertEqual(c, c2)

    def test_blob(self):
        c = Blob('hello')
        s = c.serialize()
        c2 = Blob.deserialize(s)
        self.assertEqual(c, c2)

    def test_sha(self):
        c = SHA('hola')
        s = c.serialize()
        c2 = SHA.deserialize(s)
        self.assertEqual(c, c2)

    def test_changes(self):
        c = Changes()
        c.add_created(CellName("resource1"), "resource1")
        c.add_created(CellName("resource2"), "resource2")
        c.add_deleted(CellName("resource3"), "resource3")

        c.add_modified(CellName("resource4"), Modification("resource3", "resource4"))
        c.add_rename(CellName("resource5"), CellName("resource6"))
        c.sim_limit = 23

        s = c.serialize()
        deserializer = ChangesDeserializer(CellName, str)
        c2 = deserializer.deserialize(s)
        self.assertEqual(c.created, c2.created)
        self.assertEqual(c.deleted, c2.deleted)
        self.assertEqual(c.modified, c2.modified)
        self.assertEqual(c.renames, c2.renames)

    def test_finder_result(self):
        f = FinderResult()

        s = f.serialize()
        f2 = FinderResult.deserialize(s)
        self.assertEqual(f, f2)

    def test_finder_request_unresolved(self):
        f = FinderRequest()
        f.unresolved = set([CPPDeclaration("iostream.h"), CPPDeclaration("math.h")])
        f.policy = Policy.default()
        s = f.serialize()
        f2 = FinderRequest.deserialize(s)
        self.assertEqual(f, f2)

    def test_fiunder_request_existing(self):
        f = FinderRequest()
        self.assertFalse(f)
        existing = ReferencedDependencies()
        version = BlockVersion('user/user/block/master', 1)
        existing[version][CPPDeclaration("file.h")].add(CellName("file.h"))
        f.existing = existing
        f.update = True
        f.policy = Policy.default()
        #print f
        s = f.serialize()
        #print s
        f2 = FinderRequest.deserialize(s)

        self.assertEquals(f, f2)
        self.assertTrue(f2)

    def test_brl_block(self):
        b = BRLBlock('user/user/block/master', 1)
        s = serialize(b)
        b2 = BRLBlock.deserialize(s)
        self.assertEqual(b, b2)

    def test_block_cell_name(self):
        b = BlockCellName("user/block/path/file.h")
        s = b.serialize()
        b2 = BlockCellName.deserialize(s)
        self.assertEqual(b, b2)

    def test_cell_name(self):
        b = CellName("path/to/f1.h")
        s = b.serialize()
        b2 = CellName.deserialize(s)
        self.assertEqual(b, b2)

    def test_sytem_cell_name(self):
        b = SystemCellName("iostream.h")
        s = b.serialize()
        b2 = SystemCellName.deserialize(s)
        self.assertEqual(b, b2)

    def test_block_version_table(self):
        mv = BlockVersionTable()
        mv.add_version(BlockVersion('user/user/block/master', 1))
        mv.add_version(BlockVersion('user/user/block/master', 1))
        mv.add_version(BlockVersion('user/user/block/master', 1))

        s = mv.serialize()
        mv2 = BlockVersionTable.deserialize(s)
        self.assertEqual(mv, mv2)

    def test_block_version(self):
        mv = BlockVersion('user/user/block/master', 1)
        s = mv.serialize()
        mv2 = BlockVersion.deserialize(s)
        self.assertEqual(mv, mv2)

    def test_id(self):
        rf = UserID(13)
        s = rf.serialize()
        rf2 = ID.deserialize(s)

        #print(str(rf.__class__))
        #print(str(rf2.__class__))

        self.assertEqual(rf, rf2)

    def test_reference(self):
        #With a simple CellName inside
        rf = Reference(BlockVersion('user/user/block/master', 1), CellName('f1.h'))
        s = rf.serialize()
        rf2 = Reference.deserialize(s)
        self.assertEqual(rf, rf2)

    def test_renames(self):
        r = Renames({"old.h": "new.h", "old2.h": "old3.h"})
        s = serialize(r)
        #print "S RENAMES: " + str(s)
        r2 = Renames.deserialize(s)
        self.assertEqual(r, r2)

    def test_virtual_cell(self):
        v = VirtualCell(BlockCellName('user/block/virtual.h'), "code", {"win", "nix"})
        s = v.serialize()
        v2 = CellDeserializer(BlockCellName).deserialize(s)
        self.assertEqual(v, v2)

    def test_simple_edition_cell(self):
        # Simple edition resource
        simpleresource = SimpleCell("user/block/path/to/file.h")
        simpleresource.ID = BlockCellName("user/block/path/file.h")  # CellID()
        simpleresource.root = ID()
        simpleresource.dependencies.add_implicit(BlockCellName("user/block/path/file.h"))
        simpleresource.dependencies.add_implicit(BlockCellName("user/block/path/file.h"))

        s = simpleresource.serialize()

        self.assertEqual(s[Deserializer.POLIMORPHIC_KEYWORD],
                         ClassTypedSerializer.getValue(SimpleCell))
        ob = CellDeserializer(BlockCellName).deserialize(s)
        self.assert_bii_equal(ob, simpleresource)

    def test_simple_published_cell(self):
        # Simple publish resource
        simpleresource = SimpleCell("user/block/path/to/file.h")
        simpleresource.ID = ID()
        simpleresource.root = ID()

        # Include inside "a" the "kls" attribute
        s = simpleresource.serialize()

        self.assertEqual(s[Deserializer.POLIMORPHIC_KEYWORD],
                         ClassTypedSerializer.getValue(simpleresource.__class__))
        ob = CellDeserializer(ID).deserialize(s)
        self.assert_bii_equal(simpleresource, ob)

    def test_simple_edition_cell_with_container(self):
        virtual_cell = BlockCellName('user/block/path/file.h')
        simpleresource = SimpleCell("user/block/path/to/file.h")
        simpleresource.ID = BlockCellName("user/block/path/to/file.h")
        simpleresource.root = ID()
        simpleresource.dependencies.add_implicit(BlockCellName("user/block/path/file.h"))
        simpleresource.container = virtual_cell

        s = simpleresource.serialize()

        self.assertEqual(s[Deserializer.POLIMORPHIC_KEYWORD],
                         ClassTypedSerializer.getValue(SimpleCell))
        ob = CellDeserializer(BlockCellName).deserialize(s)
        self.assert_bii_equal(ob, simpleresource)

    def test_message(self):
        m = Message("7 horses comes from Bonanza, apetecandemor", DEBUG)
        s = serialize(m)
        m2 = Message.deserialize(s)
        self.assertEqual(m, m2)

    def test_bii_response(self):
        m = BiiResponse()
        m.debug("Manamana tu tu tururu")
        m.info("Info bla bla bla")
        m.warn("Doh!!")
        m.error("Mhhhhh")

        s = serialize(m)
        #print str(s)
        m2 = BiiResponse.deserialize(s)
        #print str(m2)
        #print str(m2.serialize())
        self.assertEqual(m, m2)
