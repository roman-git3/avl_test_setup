import cocotb
from cocotb.triggers import Timer
from collections import namedtuple

from avl import Env, Driver, Monitor, Scoreboard, Transaction, List

# Simple namedtuple for stimulus (not compared by scoreboard)
AdderStim = namedtuple('AdderStim', ['a', 'b'])


class AdderTransaction(Transaction):
    """Carries the adder result; used for scoreboard comparison."""
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.sum = 0


class SimpleAdderDriver(Driver):
    def __init__(self, name, parent, dut, trigger):
        super().__init__(name, parent)
        self.dut = dut
        self.trigger = trigger  # avl.List used as sync channel to monitor

    async def run_phase(self):
        while True:
            item = await self.seq_item_port.blocking_pop()
            self.debug(f"Driving: a={item.a}, b={item.b}")
            self.dut.a.value = item.a
            self.dut.b.value = item.b
            await Timer(1, unit="ns")  # let combinational logic settle
            self.trigger.append(True)   # notify monitor to sample


class SimpleAdderMonitor(Monitor):
    def __init__(self, name, parent, dut, trigger):
        super().__init__(name, parent)
        self.dut = dut
        self.trigger = trigger

    async def run_phase(self):
        while True:
            await self.trigger.blocking_pop()
            t = AdderTransaction("adder_txn", None)
            t.sum = int(self.dut.sum.value)
            self.debug(f"Observed: sum={t.sum}")
            self.item_export.write(t)


class SimpleAdderTB(Env):
    def __init__(self, name, parent, dut):
        super().__init__(name, parent)
        self.dut = dut
        self._trigger_ = List()

        self.driver = SimpleAdderDriver("driver", self, dut, self._trigger_)
        self.monitor = SimpleAdderMonitor("monitor", self, dut, self._trigger_)
        self.scoreboard = Scoreboard("scoreboard", self)

        # connect monitor output to scoreboard actual-results port
        self.monitor.item_export.connect(self.scoreboard.after_port)

    async def run_phase(self):
        self.raise_objection()

        for a_val, b_val in [(1, 2), (5, 7), (255, 1)]:
            # push expected result to scoreboard before driving
            expected = AdderTransaction("adder_txn", None)
            expected.sum = a_val + b_val
            self.scoreboard.before_port.append(expected)

            # push stimulus to driver
            self.driver.seq_item_port.append(AdderStim(a=a_val, b=b_val))

            await Timer(10, unit="ns")

        # wait for scoreboard to finish all comparisons
        await Timer(50, unit="ns")
        self.drop_objection()


@cocotb.test()
async def avl_style_test(dut):
    tb = SimpleAdderTB("tb", None, dut)
    await tb.start()
    assert tb.scoreboard.compare_count >= 3, \
        f"Expected at least 3 comparisons, got {tb.scoreboard.compare_count}"
    dut._log.info("AVL-style test completed")
