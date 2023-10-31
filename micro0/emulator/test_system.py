import unittest

from micro0.assembler.assembler import Assembler
from micro0.emulator.computer import Memory, Cpu, CharacterOutput, Bus


class System:
    def __init__(self):
        self.memory = Memory(0x0000, [])
        self.char_out = CharacterOutput(0xf000)
        self.bus = Bus([self.memory, self.char_out])
        self.cpu = Cpu(self.bus)

    def load(self, binary):
        self.memory.contents = binary

    def run(self, cycles):
        for _ in range(cycles):
            self.cpu.tick()


class TestSystem(unittest.TestCase):
    def test_something(self):
        system = System()
        source = """
                    .org 0x0
                    load [zero]
                    store [offset]
        repeat:     load [offset]
                    store [0x000D]
                    load [0x1000]
                    brz [finished]
                    store [0xf000]
                    load [offset]
                    add [one]
                    store [offset]
                    load [zero]
                    brz [repeat]
        finished:   brz [finished]

                    .org 0x1000
        string:     db 0x48
                    db 0x65
                    db 0x6c
                    db 0x6c
                    db 0x6f
                    db 0x20
                    db 0x57
                    db 0x6f
                    db 0x72
                    db 0x6c
                    db 0x64
                    db 0x21
                    db 0x00
        zero:       db 0x00
        one:        db 0x01
        offset:     db 0x00
        """
        binary = Assembler().assemble(source)
        system.load(binary)
        system.run(1000)

        self.assertEqual("".join((chr(c) for c in system.char_out.buffer)), "Hello World!")  # add assertion here


if __name__ == '__main__':
    unittest.main()
