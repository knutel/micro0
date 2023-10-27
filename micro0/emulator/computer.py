class Memory:
    def __init__(self, contents):
        self.contents = contents

    def read(self, offset):
        return self.contents[offset]

    def write(self, offset, value):
        self.contents[offset] = value


class Cpu:
    def __init__(self, memory: Memory):
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
            self.instruction = self.memory.read(self.pc)
            self.tick_counter += 1
        elif self.tick_counter == 2:
            if self.instruction == 0x01:
                self.index = self.memory.read(self.pc + 1)
                self.tick_counter += 1
            elif self.instruction == 0x02:
                self.index = self.memory.read(self.pc + 1)
                self.tick_counter += 1
            elif self.instruction == 0x03:
                self.index = self.memory.read(self.pc + 1)
                self.tick_counter += 1
            elif self.instruction == 0x04:
                self.index = self.memory.read(self.pc + 1)
                self.tick_counter += 1
        elif self.tick_counter == 3:
            if self.instruction == 0x01:
                self.index += self.memory.read(self.pc + 2) << 8
                self.tick_counter += 1
            if self.instruction == 0x02:
                self.index += self.memory.read(self.pc + 2) << 8
                self.tick_counter += 1
            elif self.instruction == 0x03:
                self.index += self.memory.read(self.pc + 2) << 8
                self.tick_counter += 1
            elif self.instruction == 0x04:
                self.index += self.memory.read(self.pc + 2) << 8
                self.tick_counter += 1
        elif self.tick_counter == 4:
            if self.instruction == 0x01:
                self.acc = self.memory.read(self.index)
                self.pc += 3
                self.tick_counter = 0
            elif self.instruction == 0x02:
                self.memory.write(self.index, self.acc)
                self.pc += 3
                self.tick_counter = 0
            if self.instruction == 0x03:
                self.buffer = self.memory.read(self.index)
                self.tick_counter += 1
            if self.instruction == 0x04:
                if self.acc == 0:
                    self.pc = self.index
                else:
                    self.pc += 3
                self.tick_counter = 0
        elif self.tick_counter == 5:
            if self.instruction == 0x03:
                self.acc = (self.acc + self.buffer) % 0x100
                self.pc += 3
                self.tick_counter = 0

