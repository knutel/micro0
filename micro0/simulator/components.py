from myhdl import Signal, intbv, block, always, always_seq, always_comb


class Register:
    def __init__(self):
        self.data = Signal(intbv(0))

    @block
    def block(self, we, data_in, data_out, clk, reset):
        @always(clk.posedge, reset.negedge)
        def reg():
            if reset == 0:
                self.data.next = 0
                data_out.next = 0
            elif we == 1:
                self.data.next = data_in.val
                data_out.next = data_in.val

        return reg#, comb


class Memory:
    def __init__(self, initial_contents):
        self.contents = initial_contents

    @block
    def block(self, we, oe, address_in, data_bus, clk):
        data_bus_driver = data_bus.driver()

        @always(clk.posedge)
        def reg():
            if we == 1:
                self.contents[int(address_in.val)] = data_bus.val
            elif oe == 1:
                data_bus_driver.next = self.contents[int(address_in.val)]
            else:
                data_bus_driver.next = None

        return reg


class ProgramCounter:
    def __init__(self, pcl=0):
        self.pcl = Signal(intbv(pcl)[8:])
        self.pch = Signal(intbv(0)[8:])

    @block
    def block(self, wel, weh, oe, ce, data_in, address_out, clk):
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
            elif wel == 1:
                self.pcl.next = data_in.val
            elif weh == 1:
                self.pch.next = data_in.val
            if oe == 1:
                address_out.next = (self.pch.val << 8) | self.pcl.val
            else:
                address_out.next = None

        return count
