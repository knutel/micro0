class Memory:
    def __init__(self, contents):
        self.contents = contents

    def read(self, offset):
        return self.contents[offset]

    def write(self, offset, value):
        self.contents[offset] = value


class Instruction:
    def __init__(self, opcode):
        self.opcode = opcode


class LoadDirect(Instruction):
    def __init__(self):
        super().__init__(0x01)

    def tick(self, cpu):
        if cpu.tick_counter == 2:
            cpu.index = cpu.memory.read(cpu.pc + 1)
        elif cpu.tick_counter == 3:
            cpu.index += cpu.memory.read(cpu.pc + 2) << 8
        elif cpu.tick_counter == 4:
            cpu.acc = cpu.memory.read(cpu.index)
            cpu.pc += 3
            cpu.tick_counter = 0


class StoreDirect(Instruction):
    def __init__(self):
        super().__init__(0x02)

    def tick(self, cpu):
        if cpu.tick_counter == 2:
            cpu.index = cpu.memory.read(cpu.pc + 1)
        elif cpu.tick_counter == 3:
            cpu.index += cpu.memory.read(cpu.pc + 2) << 8
        elif cpu.tick_counter == 4:
            cpu.memory.write(cpu.index, cpu.acc)
            cpu.pc += 3
            cpu.tick_counter = 0


class AddDirect(Instruction):
    def __init__(self):
        super().__init__(0x03)

    def tick(self, cpu):
        if cpu.tick_counter == 2:
            cpu.index = cpu.memory.read(cpu.pc + 1)
        elif cpu.tick_counter == 3:
            cpu.index += cpu.memory.read(cpu.pc + 2) << 8
        elif cpu.tick_counter == 4:
            cpu.buffer = cpu.memory.read(cpu.index)
        elif cpu.tick_counter == 5:
            cpu.acc = (cpu.acc + cpu.buffer) % 0x100
            cpu.pc += 3
            cpu.tick_counter = 0


class BranchIfZeroSet(Instruction):
    def __init__(self):
        super().__init__(0x04)

    def tick(self, cpu):
        if cpu.tick_counter == 2:
            cpu.index = cpu.memory.read(cpu.pc + 1)
        elif cpu.tick_counter == 3:
            cpu.index += cpu.memory.read(cpu.pc + 2) << 8
        elif cpu.tick_counter == 4:
            if cpu.acc == 0:
                cpu.pc = cpu.index
            else:
                cpu.pc += 3
            cpu.tick_counter = 0


class Cpu:
    def __init__(self, memory: Memory):
        instructions = [LoadDirect(), StoreDirect(), AddDirect(), BranchIfZeroSet()]
        self.instructions = {instruction.opcode: instruction for instruction in instructions}
        assert len(instructions) == len(self.instructions)
        self.pc = 0
        self.acc = 0
        self.index = 0
        self.memory = memory
        self.tick_counter = 0
        self.instruction = None

    def tick(self):
        if self.tick_counter == 0:
            self.tick_counter += 1
        elif self.tick_counter == 1:
            opcode = self.memory.read(self.pc)
            self.instruction = self.instructions[opcode]
            self.tick_counter += 1
        else:
            self.instruction.tick(self)
            if self.tick_counter > 0:
                self.tick_counter += 1
