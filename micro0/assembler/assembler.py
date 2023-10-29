import parsita as ps


class Section:
    def __init__(self, origin, instructions):
        self.origin = origin
        self.instructions = instructions

    def __eq__(self, other):
        return self.origin == other.origin and self.instructions == other.instructions


class Instruction:
    def __init__(self, address, size, opcode):
        self.address = address
        self.size = size
        self.opcode = opcode

    def __eq__(self, other):
        return self.address == other.address and self.size == other.size and self.opcode == other.opcode


class DirectInstruction(Instruction):
    def emit(self, program, symbols, address):
        program[address] = self.opcode
        if isinstance(self.address, str):
            direct_address = symbols[self.address]
        else:
            direct_address = self.address
        program[address + 1] = direct_address & 0xff
        program[address + 2] = (direct_address >> 8) & 0xff


class LoadDirect(DirectInstruction):
    def __init__(self, address):
        super().__init__(address, 3, 0x01)


class StoreDirect(DirectInstruction):
    def __init__(self, address):
        super().__init__(address, 3, 0x02)


class AddDirect(DirectInstruction):
    def __init__(self, address):
        super().__init__(address, 3, 0x03)


class BranchIfZeroSet(DirectInstruction):
    def __init__(self, address):
        super().__init__(address, 3, 0x04)


class LiteralByte:
    def __init__(self, value):
        self.value = value
        self.size = 1

    def __eq__(self, other):
        return self.value == other.value and self.size == other.size

    def emit(self, program, symbols, address):
        program[address] = self.value


class Label:
    def __init__(self, value):
        self.value = value
        self.size = 0

    def __eq__(self, other):
        return self.value == other.value

    def emit(self, program, symbols, address):
        pass


def flatten(items):
    output = []
    for item in items:
        if isinstance(item, list):
            output.extend(item)
        else:
            output.append(item)
    return output


class AssemblerParsers(ps.ParserContext, whitespace=r"[ \n]*"):
    hexadecimal = ps.lit("0x") >> ps.reg(r"[0-9a-fA-F]+") > (lambda x: int(x, 16))
    origin = ps.lit(".org") >> hexadecimal
    label = ps.reg(r"[a-z]+") > str
    direct_address = ps.lit("[") >> (hexadecimal | label) << ps.lit("]")
    load_direct = ps.lit("load") >> direct_address > LoadDirect
    store_direct = ps.lit("store") >> direct_address > StoreDirect
    add_direct = ps.lit("add") >> direct_address > AddDirect
    branch_if_zero_set_direct = ps.lit("brz") >> direct_address > BranchIfZeroSet
    literal_byte = ps.lit("db") >> hexadecimal > LiteralByte
    instructions = load_direct | store_direct | add_direct | branch_if_zero_set_direct | literal_byte
    label_definition = label << ps.lit(":") > Label
    instructions_with_label = label_definition & instructions
    instruction = instructions_with_label | instructions
    section = origin & ps.rep1(instruction) > (lambda x: Section(x[0], flatten(x[1])))
    program = ps.rep1(section)


class Emittable:
    def __init__(self, address, instruction):
        self.address = address
        self.instruction = instruction

    def emit(self, program, symbols):
        self.instruction.emit(program, symbols, self.address)


class Assembler:
    def assemble(self, source):
        result = AssemblerParsers.program.parse(source)
        match result:
            case ps.Success(value):
                sections = value
            case ps.Failure(error):
                raise error
        global_max_address = 0
        symbols = {}
        for section in sections:
            max_address = section.origin
            for instruction in section.instructions:
                if isinstance(instruction, Label):
                    symbols[instruction.value] = max_address
                max_address += instruction.size
            global_max_address = max(global_max_address, max_address)
        program = [0] * global_max_address
        emittables = []
        for section in sections:
            address = section.origin
            for instruction in section.instructions:
                emittables.append(Emittable(address, instruction))
                address += instruction.size
        for emittable in emittables:
            emittable.emit(program, symbols)

        return program
