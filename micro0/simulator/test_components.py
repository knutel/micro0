import unittest

from myhdl import block, Signal, intbv, always, TristateSignal, delay, instance, StopSimulation

from micro0.simulator.components import Register


class TestMemory(unittest.TestCase):
    def test_register_input(self):
        @block
        def testbench():
            reg_a_ie = Signal(bool(0))
            reg_a_oe = Signal(bool(0))

            bus = TristateSignal(intbv(0)[8:])
            bus_stim = bus.driver()
            clk = Signal(bool(0))

            HALF_PERIOD = delay(10)

            reg = Register()
            reg_a = reg.block(reg_a_ie, reg_a_oe, bus, bus.driver(), clk)

            @always(HALF_PERIOD)
            def clkgen():
                clk.next = not clk

            @instance
            def stimulus():
                yield delay(0)
                bus_stim.next = 123
                yield clk.posedge
                yield clk.negedge
                reg_a_ie.next = 1
                yield clk.posedge
                yield clk.negedge
                reg_a_ie.next = 0
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
            reg_a_ie = Signal(bool(0))
            reg_a_oe = Signal(bool(0))

            bus = TristateSignal(intbv(0)[8:])
            bus_stim = bus.driver()
            clk = Signal(bool(0))

            HALF_PERIOD = delay(10)

            reg = Register()
            reg_a = reg.block(reg_a_ie, reg_a_oe, bus, bus.driver(), clk)

            @always(HALF_PERIOD)
            def clkgen():
                clk.next = not clk

            @instance
            def stimulus():
                yield delay(0)
                reg.data.next = 42
                yield clk.posedge
                yield clk.negedge
                reg_a_oe.next = 1
                yield clk.posedge
                self.assertEqual(bus.val, 42)
                yield clk.negedge
                reg_a_oe.next = 0
                yield clk.posedge
                self.assertIsNone(bus.val)
                raise StopSimulation

            return clkgen, stimulus, reg_a

        tb = testbench()
        tb.config_sim(trace=True)
        tb.run_sim()


if __name__ == '__main__':
    unittest.main()
