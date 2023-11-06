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
