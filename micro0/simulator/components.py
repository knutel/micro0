from myhdl import Signal, intbv, block, always, always_comb


class Register:
    def __init__(self):
        self.data = Signal(intbv(0))

    @block
    def block(self, ie, oe, data_in, data_out, clk):
        @always(clk.posedge)
        def reg():
            if ie == 1:
                self.data.next = data_in.val

        @always_comb
        def comb():
            if oe == 1:
                data_out.next = self.data.val
            else:
                data_out.next = None

        return reg, comb


class Memory:
    def __init__(self, initial_contents):
        self.contents = initial_contents
        self.address = Signal(intbv(0))

    @block
    def block(self, ale, ie, oe, address_in, data_in, data_out, clk):
        @always(clk.posedge)
        def reg():
            if ale == 1:
                self.address.next = address_in.val
            if ie == 1:
                self.contents[int(self.address.val)] = data_in.val

        @always_comb
        def comb():
            if oe == 1:
                data_out.next = self.contents[int(self.address.val)]
            else:
                data_out.next = None

        return reg, comb


class ProgramCounter:
    def __init__(self, pcl=0):
        self.pcl = Signal(intbv(pcl)[8:])
        self.pch = Signal(intbv(0)[8:])
        self.pcl_latch = Signal(intbv(pcl)[8:])
        self.pch_latch = Signal(intbv(0)[8:])

    @block
    def block(self, iel, ieh, lel, leh, oe, ce, data_in, address_out, clk):
        @always(clk.posedge)
        def count():
            if ce == 1:
                if self.pcl.val == 255:
                    self.pcl.next = 0
                    if self.pch.val == 255:
                        self.pch.next = 0
                    else:
                        self.pch.next = self.pch.val + 1
                else:
                    self.pcl.next = self.pcl.val + 1
            elif iel == 1:
                self.pcl_latch.next = data_in.val
            elif ieh == 1:
                self.pch_latch.next = data_in.val
            if lel == 1:
                self.pcl.next = self.pcl_latch.val
            if leh == 1:
                self.pch.next = self.pch_latch.val

        @always_comb
        def comb():
            if oe == 1:
                address_out.next = (self.pch.val << 8) | self.pcl.val
            else:
                address_out.next = None

        return comb, count
