import unittest

from micro0.emulator.computer import Memory, Cpu


class TestCpu(unittest.TestCase):
    def test_reset(self):
        memory = Memory([])
        cpu = Cpu(memory)
        self.assertEqual(0, cpu.acc)
        self.assertEqual(0, cpu.pc)

    def test_load_immediate(self):
        memory = Memory([0x01, 0x25])
        cpu = Cpu(memory)
        cpu.tick()
        cpu.tick()
        cpu.tick()
        self.assertEqual(0x25, cpu.acc)

    def test_store_absolute(self):
        memory = Memory([0x02, 0x04, 0, 0, 0])
        cpu = Cpu(memory)
        cpu.acc = 0x33
        cpu.tick()
        cpu.tick()
        cpu.tick()
        cpu.tick()
        self.assertEqual(0x33, memory.read(0x04))


if __name__ == '__main__':
    unittest.main()
