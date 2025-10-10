import unittest

from myhdl import block, Signal, intbv, always, TristateSignal, delay, instance, StopSimulation, ResetSignal

from micro0.simulator.components import Register, Memory, ProgramCounter


class TestRegister(unittest.TestCase):
    def test_register_input(self):
        @block
        def testbench():
            we = Signal(bool(0))

            data_bus_in = TristateSignal(intbv(0)[8:])
            data_bus_in_stim = data_bus_in.driver()
            data_bus_out = TristateSignal(intbv(0)[8:])
            clk = Signal(bool(0))
            reset = ResetSignal(0, active=0, isasync=True)

            HALF_PERIOD = delay(10)
            ACTIVE_LOW, INACTIVE_HIGH = 0, 1

            reg = Register()
            reg_a = reg.block(we, data_bus_in, data_bus_out.driver(), clk, reset)

            @always(HALF_PERIOD)
            def clkgen():
                clk.next = not clk

            @instance
            def stimulus():
                reset.next = ACTIVE_LOW
                data_bus_in_stim.next = 0x10
                yield clk.negedge
                reset.next = INACTIVE_HIGH
                yield clk.posedge
                we.next = 1
                yield clk.posedge
                data_bus_in_stim.next = 0x0C
                we.next = 0
                yield clk.posedge
                self.assertEqual(reg.data.val, 0x10)
                yield clk.posedge
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

            data_bus = TristateSignal(intbv(0)[8:])
            data_bus_stim = data_bus.driver()
            address_bus = Signal(intbv(0)[16:])
            clk = Signal(bool(0))

            HALF_PERIOD = delay(10)

            mem = Memory([43, 100, 39])
            mem_a = mem.block(ie, oe, address_bus, data_bus, clk)

            @always(HALF_PERIOD)
            def clkgen():
                clk.next = not clk

            @instance
            def stimulus():
                address_bus.next = 1
                ie.next = 1
                data_bus_stim.next = 42

                yield clk.posedge
                yield clk.posedge
                ie.next = 0
                oe.next = 1
                
                data_bus_stim.next = None
                yield clk.negedge
                yield clk.posedge
                yield delay(1)
                self.assertEqual(data_bus.val, 42)
                self.assertEqual(mem.contents[1], 42)

                yield clk.posedge

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

            data_bus = TristateSignal(intbv(0)[8:])
            data_bus_stim = data_bus.driver()
            address_bus = Signal(intbv(0)[16:])
            clk = Signal(bool(0))

            HALF_PERIOD = delay(10)

            mem = Memory([43, 100, 39])
            mem_a = mem.block(ie, oe, address_bus, data_bus, clk)

            @always(HALF_PERIOD)
            def clkgen():
                clk.next = not clk

            @instance
            def stimulus():
                yield clk.posedge
                address_bus.next = 2
                oe.next = 1
                yield clk.posedge
                oe.next = 0
                yield delay(1)
                self.assertEqual(data_bus.val, 39)
                yield clk.posedge
                data_bus_stim.next = 23
                ie.next = 1
                address_bus.next = 1
                yield clk.posedge
                self.assertEqual(mem.contents[1], 23)
                ie.next = 0
                oe.next = 1
                data_bus_stim.next = None
                address_bus.next = 0

                yield clk.posedge
                yield delay(1)
                self.assertEqual(data_bus.val, 43)
                yield clk.posedge
                raise StopSimulation

            return clkgen, stimulus, mem_a

        tb = testbench()
        tb.config_sim(trace=True)
        tb.run_sim()


class TestProgramCounter(unittest.TestCase):
    def test_increment_from_zero(self):
        @block
        def testbench():
            wel = Signal(bool(0))
            weh = Signal(bool(0))
            oe = Signal(bool(0))
            ce = Signal(bool(0))

            data_bus = TristateSignal(intbv(0)[8:])
            data_bus_stim = data_bus.driver()
            address_bus = TristateSignal(intbv(0)[16:])
            address_bus_stim = data_bus.driver()
            clk = Signal(bool(0))

            HALF_PERIOD = delay(10)


            pc = ProgramCounter()
            pc_inst = pc.block(wel, weh, oe, ce, data_bus, address_bus.driver(), clk)

            @always(HALF_PERIOD)
            def clkgen():
                clk.next = not clk

            @instance
            def stimulus():
                yield clk.posedge
                oe.next = 1
                ce.next = 1
                self.assertIsNone(data_bus.val)

                yield clk.posedge
                ce.next = 0

                yield delay(1)
                self.assertEqual(0, address_bus.val)
                
                yield clk.posedge
                oe.next = 0

                yield delay(1)
                self.assertEqual(1, address_bus.val)
                
                yield clk.posedge

                yield delay(1)
                self.assertIsNone(address_bus.val)

                yield clk.posedge

                raise StopSimulation

            return clkgen, stimulus, pc_inst

        tb = testbench()
        tb.config_sim(trace=True)
        tb.run_sim()

    def test_wrap_pcl(self):
        @block
        def testbench():
            wel = Signal(bool(0))
            weh = Signal(bool(0))
            ce = Signal(bool(0))
            oe = Signal(bool(0))

            data_bus = TristateSignal(intbv(0)[8:])
            data_bus_stim = data_bus.driver()
            address_bus = TristateSignal(intbv(0)[16:])
            address_bus_stim = data_bus.driver()
            clk = Signal(bool(0))

            HALF_PERIOD = delay(10)


            pc = ProgramCounter(255)
            pc_inst = pc.block(wel, weh, oe, ce, data_bus, address_bus.driver(), clk)

            @always(HALF_PERIOD)
            def clkgen():
                clk.next = not clk

            @instance
            def stimulus():
                oe.next = 1
                ce.next = 1
                yield clk.posedge
                yield clk.posedge
                yield clk.posedge
                delay(1)
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
            wel = Signal(bool(0))
            weh = Signal(bool(0))
            ce = Signal(bool(0))
            oe = Signal(bool(0))

            data_bus = TristateSignal(intbv(0)[8:])
            data_bus_stim = data_bus.driver()
            address_bus = TristateSignal(intbv(0)[16:])
            address_bus_stim = data_bus.driver()
            clk = Signal(bool(0))

            HALF_PERIOD = delay(10)


            pc = ProgramCounter()
            pc_inst = pc.block(wel, weh, oe, ce, data_bus, address_bus.driver(), clk)

            @always(HALF_PERIOD)
            def clkgen():
                clk.next = not clk

            @instance
            def stimulus():
                wel.next = 1
                data_bus_stim.next = 0x12

                yield clk.posedge
                weh.next = 1
                wel.next = 0
                data_bus_stim.next = 0x34

                yield clk.posedge
                weh.next = 0
                data_bus_stim.next = None
                oe.next = 1

                yield clk.posedge
                oe.next = 0

                yield delay(1)
                self.assertEqual(0x3412, address_bus.val)

                yield clk.posedge
                self.assertIsNone(data_bus.val)

                raise StopSimulation

            return clkgen, stimulus, pc_inst

        tb = testbench()
        tb.config_sim(trace=True)
        tb.run_sim()


if __name__ == '__main__':
    unittest.main()
