import cocotb
from cocotb.triggers import Timer

from avl import Env, Driver, Monitor, Scoreboard, Transaction, List, Uint8, Uint


class AdderTransaction(Transaction):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.a   = Uint8(0)                   # 8-bit input — randomized
        self.b   = Uint8(0)                   # 8-bit input — randomized
        self.sum = Uint(0, width=9, auto_random=False)  # 9-bit output — predicted, not randomized
        # inputs are stimulus only — exclude from scoreboard comparison
        self.set_field_attributes("a", compare=False)
        self.set_field_attributes("b", compare=False)


class SimpleAdderScoreboard(Scoreboard):
    async def run_phase(self):
        while True:
            self.before_item = await self.before_port.blocking_pop()
            self.after_item  = await self.after_port.blocking_pop()

            # predict expected sum from stimulus fields
            self.before_item.sum.value = (
                self.before_item.a.value + self.before_item.b.value
            )

            self.before_item.compare(self.after_item, verbose=self.verbose, bidirectional=True)
            self.compare_count += 1
            self.before_item = None
            self.after_item  = None


class SimpleAdderDriver(Driver):
    def __init__(self, name, parent, dut, trigger):
        super().__init__(name, parent)
        self.dut = dut
        self.trigger = trigger  # avl.List used as sync channel to monitor

    async def run_phase(self):
        while True:
            item = await self.seq_item_port.blocking_pop()
            self.debug(f"Driving: a={item.a.value}, b={item.b.value}")
            self.dut.a.value = item.a.value
            self.dut.b.value = item.b.value
            await Timer(1, unit="ns")  # let combinational logic settle
            self.trigger.append(True)  # notify monitor to sample


class SimpleAdderMonitor(Monitor):
    def __init__(self, name, parent, dut, trigger):
        super().__init__(name, parent)
        self.dut = dut
        self.trigger = trigger

    async def run_phase(self):
        while True:
            await self.trigger.blocking_pop()
            t = AdderTransaction("adder_txn", None)
            t.sum.value = int(self.dut.sum.value)
            self.debug(f"Observed: sum={t.sum.value}")
            self.item_export.write(t)


class SimpleAdderTB(Env):
    def __init__(self, name, parent, dut):
        super().__init__(name, parent)
        self.dut = dut
        self._trigger_ = List()

        self.driver     = SimpleAdderDriver("driver", self, dut, self._trigger_)
        self.monitor    = SimpleAdderMonitor("monitor", self, dut, self._trigger_)
        self.scoreboard = SimpleAdderScoreboard("scoreboard", self)
        self.scoreboard.set_min_compare_count(3)

        # connect monitor output to scoreboard actual-results port
        self.monitor.item_export.connect(self.scoreboard.after_port)

    async def run_phase(self):
        self.raise_objection()

        for _ in range(15):
            stim = AdderTransaction("adder_txn", None)
            stim.randomize()  # randomizes a and b; sum is auto_random=False
            self.debug(f"Randomized stimulus: a={stim.a.value}, b={stim.b.value}")

            # stim goes to scoreboard (for prediction) and driver (for DUT)
            self.scoreboard.before_port.append(stim)
            self.driver.seq_item_port.append(stim)

            await Timer(10, unit="ns")

        # wait for scoreboard to finish all comparisons
        await Timer(50, unit="ns")
        self.drop_objection()


@cocotb.test()
async def avl_style_test(dut):
    tb = SimpleAdderTB("tb", None, dut)
    await tb.start()
    dut._log.info("AVL-style test completed")