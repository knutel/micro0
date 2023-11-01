from typing import List


class Memory:
    def __init__(self, offset, contents):
        self.offset = offset
        self.contents = contents

    def read(self, offset):
        return self.contents[offset]

    def write(self, offset, value):
        self.contents[offset] = value


class CharacterOutput:
    def __init__(self, offset):
        self.offset = offset
        self.buffer = []

    def write(self, offset, value):
        self.buffer.append(value)


class Instruction:
    def __init__(self, opcode):
        self.opcode = opcode


class LoadDirect(Instruction):
    def __init__(self):
        super().__init__(0x01)

    def tick(self, cpu):
        if cpu.tick_counter == 2:
            cpu.index = cpu.bus.read(cpu.pc + 1)
        elif cpu.tick_counter == 3:
            cpu.index += cpu.bus.read(cpu.pc + 2) << 8
        elif cpu.tick_counter == 4:
            cpu.acc = cpu.bus.read(cpu.index)
            cpu.pc += 3
            cpu.tick_counter = 0


class StoreDirect(Instruction):
    def __init__(self):
        super().__init__(0x02)

    def tick(self, cpu):
        if cpu.tick_counter == 2:
            cpu.index = cpu.bus.read(cpu.pc + 1)
        elif cpu.tick_counter == 3:
            cpu.index += cpu.bus.read(cpu.pc + 2) << 8
        elif cpu.tick_counter == 4:
            cpu.bus.write(cpu.index, cpu.acc)
            cpu.pc += 3
            cpu.tick_counter = 0


class AddDirect(Instruction):
    def __init__(self):
        super().__init__(0x03)

    def tick(self, cpu):
        if cpu.tick_counter == 2:
            cpu.index = cpu.bus.read(cpu.pc + 1)
        elif cpu.tick_counter == 3:
            cpu.index += cpu.bus.read(cpu.pc + 2) << 8
        elif cpu.tick_counter == 4:
            cpu.buffer = cpu.bus.read(cpu.index)
        elif cpu.tick_counter == 5:
            cpu.acc = (cpu.acc + cpu.buffer) % 0x100
            cpu.pc += 3
            cpu.tick_counter = 0


class BranchIfZeroSet(Instruction):
    def __init__(self):
        super().__init__(0x04)

    def tick(self, cpu):
        if cpu.tick_counter == 2:
            cpu.index = cpu.bus.read(cpu.pc + 1)
        elif cpu.tick_counter == 3:
            cpu.index += cpu.bus.read(cpu.pc + 2) << 8
        elif cpu.tick_counter == 4:
            if cpu.acc == 0:
                cpu.pc = cpu.index
            else:
                cpu.pc += 3
            cpu.tick_counter = 0


class Bus:
    def __init__(self, devices):
        self.devices = devices[:]
        self.devices.sort(key=lambda device: -device.offset)

    def read(self, offset):
        for device in self.devices:
            if offset >= device.offset:
                return device.read(offset)

    def write(self, offset, value):
        for device in self.devices:
            if offset >= device.offset:
                device.write(offset, value)
                return


class Cpu:
    def __init__(self, bus: Bus):
        instructions = [LoadDirect(), StoreDirect(), AddDirect(), BranchIfZeroSet()]
        self.instructions = {instruction.opcode: instruction for instruction in instructions}
        assert len(instructions) == len(self.instructions)
        self.pc = 0
        self.acc = 0
        self.index = 0
        self.bus = bus
        self.tick_counter = 0
        self.instruction = None

    def tick(self, ticks=1):
        for _ in range(ticks):
            self._tick()

    def _tick(self):
        if self.tick_counter == 0:
            self.tick_counter += 1
        elif self.tick_counter == 1:
            opcode = self.bus.read(self.pc)
            self.instruction = self.instructions[opcode]
            self.tick_counter += 1
        else:
            self.instruction.tick(self)
            if self.tick_counter > 0:
                self.tick_counter += 1


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
