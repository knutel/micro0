import unittest

from micro0.emulator.computer import Memory, Cpu


class TestCpu(unittest.TestCase):
    def test_reset(self):
        memory = Memory([])
        cpu = Cpu(memory)
        self.assertEqual(0, cpu.acc)
        self.assertEqual(0, cpu.pc)

    def test_load_direct(self):
        memory = Memory([0x01, 0x05, 0, 0, 0, 0x09])
        cpu = Cpu(memory)
        cpu.tick()
        cpu.tick()
        cpu.tick()
        cpu.tick()
        cpu.tick()
        self.assertEqual(0x09, cpu.acc)

    def test_store_direct(self):
        memory = Memory([0x02, 0x04, 0, 0, 0])
        cpu = Cpu(memory)
        cpu.acc = 0x33
        cpu.tick()
        cpu.tick()
        cpu.tick()
        cpu.tick()
        cpu.tick()
        self.assertEqual(0x33, memory.read(0x04))

    def test_add_direct(self):
        memory = Memory([0x03, 0x03, 0x00, 0x13])
        cpu = Cpu(memory)
        cpu.acc = 0x32
        cpu.tick()
        cpu.tick()
        cpu.tick()
        cpu.tick()
        cpu.tick()
        cpu.tick()
        self.assertEqual(0x45, cpu.acc)

    def test_branch_if_zero_immediate_false(self):
        memory = Memory([0x04, 0x0f, 0x00, 0x00])
        cpu = Cpu(memory)
        cpu.acc = 0x02
        cpu.tick()
        cpu.tick()
        cpu.tick()
        cpu.tick()
        cpu.tick()
        self.assertEqual(0x0003, cpu.pc)

    def test_branch_if_zero_immediate_true(self):
        memory = Memory([0x04, 0x0f, 0x00, 0x00])
        cpu = Cpu(memory)
        cpu.acc = 0x00
        cpu.tick()
        cpu.tick()
        cpu.tick()
        cpu.tick()
        cpu.tick()
        self.assertEqual(0x000f, cpu.pc)


if __name__ == '__main__':
    unittest.main()
