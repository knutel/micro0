import unittest

from myhdl import block, Signal, intbv, always, TristateSignal, delay, instance, StopSimulation

from micro0.simulator.components import Register, Memory, ProgramCounter


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


class TestProgramCounter(unittest.TestCase):
    def test_increment_from_zero(self):
        @block
        def testbench():
            iel = Signal(bool(0))
            ieh = Signal(bool(0))
            lel = Signal(bool(0))
            leh = Signal(bool(0))
            ce = Signal(bool(0))
            oe = Signal(bool(0))

            data_bus = TristateSignal(intbv(0)[8:])
            data_bus_stim = data_bus.driver()
            address_bus = TristateSignal(intbv(0)[16:])
            address_bus_stim = data_bus.driver()
            clk = Signal(bool(0))

            HALF_PERIOD = delay(10)


            pc = ProgramCounter()
            pc_inst = pc.block(iel, ieh, lel, leh, oe, ce, data_bus, address_bus.driver(), clk)

            @always(HALF_PERIOD)
            def clkgen():
                clk.next = not clk

            @instance
            def stimulus():
                yield clk.negedge
                oe.next = 1
                self.assertIsNone(data_bus.val)
                yield clk.posedge
                self.assertEqual(0, address_bus.val)
                yield clk.negedge
                oe.next = 0
                ce.next = 1
                yield clk.negedge
                oe.next = 1
                ce.next = 0
                yield clk.posedge
                self.assertEqual(1, address_bus.val)

                raise StopSimulation

            return clkgen, stimulus, pc_inst

        tb = testbench()
        tb.config_sim(trace=True)
        tb.run_sim()

    def test_wrap_pcl(self):
        @block
        def testbench():
            iel = Signal(bool(0))
            ieh = Signal(bool(0))
            lel = Signal(bool(0))
            leh = Signal(bool(0))
            ce = Signal(bool(0))
            oe = Signal(bool(0))

            data_bus = TristateSignal(intbv(0)[8:])
            data_bus_stim = data_bus.driver()
            address_bus = TristateSignal(intbv(0)[16:])
            address_bus_stim = data_bus.driver()
            clk = Signal(bool(0))

            HALF_PERIOD = delay(10)


            pc = ProgramCounter(255)
            pc_inst = pc.block(iel, ieh, lel, leh, oe, ce, data_bus, address_bus.driver(), clk)

            @always(HALF_PERIOD)
            def clkgen():
                clk.next = not clk

            @instance
            def stimulus():
                yield clk.negedge
                oe.next = 0
                ce.next = 1
                yield clk.negedge
                oe.next = 1
                ce.next = 0
                yield clk.posedge
                self.assertEqual(0x0100, address_bus.val)
                yield clk.negedge
                oe.next = 0
                yield clk.negedge

                raise StopSimulation

            return clkgen, stimulus, pc_inst

        tb = testbench()
        tb.config_sim(trace=True)
        tb.run_sim()

    def test_input(self):
        @block
        def testbench():
            iel = Signal(bool(0))
            ieh = Signal(bool(0))
            lel = Signal(bool(0))
            leh = Signal(bool(0))
            ce = Signal(bool(0))
            oe = Signal(bool(0))

            data_bus = TristateSignal(intbv(0)[8:])
            data_bus_stim = data_bus.driver()
            address_bus = TristateSignal(intbv(0)[16:])
            address_bus_stim = data_bus.driver()
            clk = Signal(bool(0))

            HALF_PERIOD = delay(10)


            pc = ProgramCounter()
            pc_inst = pc.block(iel, ieh, lel, leh, oe, ce, data_bus, address_bus.driver(), clk)

            @always(HALF_PERIOD)
            def clkgen():
                clk.next = not clk

            @instance
            def stimulus():
                yield clk.negedge
                iel.next = 1
                data_bus_stim.next = 0x12
                yield clk.negedge
                iel.next = 0
                ieh.next = 1
                data_bus_stim.next = 0x34
                yield clk.negedge
                ieh.next = 0
                data_bus_stim.next = None
                lel.next = 1
                leh.next = 1
                yield clk.negedge
                lel.next = 0
                leh.next = 0
                oe.next = 1
                yield clk.negedge
                self.assertEqual(0x3412, address_bus.val)
                oe.next = 0
                yield clk.negedge
                self.assertIsNone(data_bus.val)

                raise StopSimulation

            return clkgen, stimulus, pc_inst

        tb = testbench()
        tb.config_sim(trace=True)
        tb.run_sim()


if __name__ == '__main__':
    unittest.main()
