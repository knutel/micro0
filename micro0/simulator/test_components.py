import unittest

from myhdl import block, Signal, intbv, always, TristateSignal, delay, instance, StopSimulation

from micro0.simulator.components import Register, Memory


class TestRegister(unittest.TestCase):
    def test_register_input(self):
        @block
        def testbench():
            ie = Signal(bool(0))
            oe = Signal(bool(0))

            data_bus = TristateSignal(intbv(0)[8:])
            data_bus_stim = data_bus.driver()
            clk = Signal(bool(0))

            HALF_PERIOD = delay(10)

            reg = Register()
            reg_a = reg.block(ie, oe, data_bus, data_bus.driver(), clk)

            @always(HALF_PERIOD)
            def clkgen():
                clk.next = not clk

            @instance
            def stimulus():
                yield delay(0)
                data_bus_stim.next = 123
                yield clk.posedge
                yield clk.negedge
                ie.next = 1
                yield clk.posedge
                yield clk.negedge
                ie.next = 0
                yield clk.posedge
                yield clk.posedge
                self.assertEqual(reg.data.val, 123)
                raise StopSimulation

            return clkgen, stimulus, reg_a

        tb = testbench()
        tb.config_sim(trace=True)
        tb.run_sim()

    def test_register_output(self):
        @block
        def testbench():
            ie = Signal(bool(0))
            oe = Signal(bool(0))

            data_bus = TristateSignal(intbv(0)[8:])
            data_bus_stim = data_bus.driver()
            clk = Signal(bool(0))

            HALF_PERIOD = delay(10)

            reg = Register()
            reg_a = reg.block(ie, oe, data_bus, data_bus.driver(), clk)

            @always(HALF_PERIOD)
            def clkgen():
                clk.next = not clk

            @instance
            def stimulus():
                yield delay(0)
                reg.data.next = 42
                yield clk.posedge
                yield clk.negedge
                oe.next = 1
                yield clk.posedge
                self.assertEqual(data_bus.val, 42)
                yield clk.negedge
                oe.next = 0
                yield clk.posedge
                self.assertIsNone(data_bus.val)
                raise StopSimulation

            return clkgen, stimulus, reg_a

        tb = testbench()
        tb.config_sim(trace=True)
        tb.run_sim()


class TestMemory(unittest.TestCase):
    def test_memory_input(self):
        @block
        def testbench():
            ie = Signal(bool(0))
            oe = Signal(bool(0))
            ale = Signal(bool(0))

            data_bus = TristateSignal(intbv(0)[8:])
            data_bus_stim = data_bus.driver()
            address_bus = Signal(intbv(0)[16:])
            clk = Signal(bool(0))

            HALF_PERIOD = delay(10)

            mem = Memory([43, 100, 39])
            mem_a = mem.block(ale, ie, oe, address_bus, data_bus, data_bus.driver(), clk)

            @always(HALF_PERIOD)
            def clkgen():
                clk.next = not clk

            @instance
            def stimulus():
                yield clk.negedge
                ale.next = 1
                address_bus.next = 1
                yield clk.negedge
                ale.next = 0
                ie.next = 1
                data_bus_stim.next = 42
                yield clk.negedge
                ie.next = 0
                yield clk.posedge
                self.assertEqual(mem.contents[1], 42)
                raise StopSimulation

            return clkgen, stimulus, mem_a

        tb = testbench()
        tb.config_sim(trace=True)
        tb.run_sim()

    def test_memory_output(self):
        @block
        def testbench():
            ie = Signal(bool(0))
            oe = Signal(bool(0))
            ale = Signal(bool(0))

            data_bus = TristateSignal(intbv(0)[8:])
            data_bus_stim = data_bus.driver()
            address_bus = Signal(intbv(0)[16:])
            clk = Signal(bool(0))

            HALF_PERIOD = delay(10)

            mem = Memory([43, 100, 39])
            mem_a = mem.block(ale, ie, oe, address_bus, data_bus, data_bus.driver(), clk)

            @always(HALF_PERIOD)
            def clkgen():
                clk.next = not clk

            @instance
            def stimulus():
                yield clk.negedge
                ale.next = 1
                address_bus.next = 2
                yield clk.negedge
                ale.next = 0
                oe.next = 1
                yield clk.posedge
                self.assertEqual(data_bus.val, 39)
                yield clk.negedge
                oe.next = 0
                yield clk.posedge
                self.assertIsNone(data_bus.val)
                raise StopSimulation

            return clkgen, stimulus, mem_a

        tb = testbench()
        tb.config_sim(trace=True)
        tb.run_sim()


if __name__ == '__main__':
    unittest.main()
