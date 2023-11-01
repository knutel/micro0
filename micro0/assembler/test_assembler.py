import unittest
import parsita as ps

from micro0.assembler.assembler import Section, LoadDirect, StoreDirect, Label, AssemblerParsers, Assembler


class TestParser(unittest.TestCase):
    def test_hexadecimal(self):
        self.assertEqual(ps.Success(0x1234), AssemblerParsers.hexadecimal.parse("0x1234"))

    def test_origin(self):
        self.assertEqual(ps.Success(0x1234), AssemblerParsers.origin.parse(".org 0x1234"))

    def test_load_direct(self):
        self.assertEqual(ps.Success(LoadDirect(0x1234)), AssemblerParsers.load_direct.parse("load [0x1234]"))

    def test_store_direct(self):
        self.assertEqual(ps.Success(StoreDirect(0x1234)), AssemblerParsers.store_direct.parse("store [0x1234]"))

    def test_label_definition(self):
        self.assertEqual(ps.Success([Label("loop"), StoreDirect(0x1234)]), AssemblerParsers.instruction.parse("loop: store [0x1234]"))

    def test_section(self):
        self.assertEqual(ps.Success(Section(0, [LoadDirect(0x1234), StoreDirect(0x4321)])),
                         AssemblerParsers.section.parse(".org 0x0\nload [0x1234]\nstore [0x4321]"))


class TestAssembler(unittest.TestCase):
    def test_simple(self):
        source = """
        .org 0x0
        load [0x0003]
        .org 0x0003
        db 0x32
        """
        assembler = Assembler()
        prog = assembler.assemble(source)
        self.assertEqual([0x01, 0x03, 0x00, 0x32], prog)

    def test_move_with_label(self):
        source = """
                .org 0x0
                load [source]
                store [dest]
                
                .org 0x0006
        source: db 0x32
        dest:   db 0x0
        """
        assembler = Assembler()
        prog = assembler.assemble(source)
        self.assertEqual([0x01, 0x06, 0x00, 0x02, 0x07, 0x00, 0x32, 0x00], prog)

    def test_loop_with_label(self):
        source = """
                .org 0x0
        repeat: load [source] /* comment */
                store [dest]
                brz [repeat]
                
                .org 0x0009
        source: db 0x32
        dest:   db 0x0
        """
        assembler = Assembler()
        prog = assembler.assemble(source)
        self.assertEqual([0x01, 0x09, 0x00, 0x02, 0x0a, 0x00, 0x04, 0x00, 0x00, 0x32, 0x00], prog)

    def test_add(self):
        source = """
                .org 0x0
        repeat: load [a]
                add [b]
                brz [repeat]
                .org 0x0009
        a:      db 0x32
        b:      db 0x0
        """
        assembler = Assembler()
        prog = assembler.assemble(source)
        self.assertEqual([0x01, 0x09, 0x00, 0x03, 0x0a, 0x00, 0x04, 0x00, 0x00, 0x32, 0x00], prog)


if __name__ == '__main__':
    unittest.main()
