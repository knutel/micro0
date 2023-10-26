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
                self.acc = self.memory.read(self.pc + 1)
                self.pc += 2
                self.tick_counter = 0
            elif self.instruction == 0x02:
                self.index = self.memory.read(self.pc + 1)
                self.tick_counter += 1
        elif self.tick_counter == 3:
            if self.instruction == 0x02:
                self.memory.write(self.index, self.acc)
                self.pc += 3
                self.tick_counter = 0
