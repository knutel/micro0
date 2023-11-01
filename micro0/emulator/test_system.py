import unittest

from micro0.assembler.assembler import Assembler
from micro0.emulator.computer import System


class TestSystem(unittest.TestCase):
    def test_something(self):
        system = System()
        source = """
                    .org 0x0
                    load [zero]
                    store [index]   /* Initialize index */
        repeat:     load [index]
                    store [0x000D]  /* Store the index lsb at (i + 1) */
        i:          load [0x1000]   /* Effectively 0x1000 + index. Self modifying code. */
                    brz [finished]
                    store [0xf000]  /* Write to character device */
                    load [index]
                    add [one]       /* Increment index */
                    store [index]
                    load [zero]     /* Unconditional jump */
                    brz [repeat]
        finished:   brz [finished]  /* Loop forever */

                    .org 0x1000
        string:     db 0x48         /* "Hello World!" */
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
                    db 0x00 /* null terminator */
        zero:       db 0x00
        one:        db 0x01
        index:      db 0x00 /* index into the string */
        """
        binary = Assembler().assemble(source)
        system.load(binary)
        system.run(1000)

        self.assertEqual("".join((chr(c) for c in system.char_out.buffer)), "Hello World!")  # add assertion here


if __name__ == '__main__':
    unittest.main()
