import cocotb
from cocotb.triggers import Timer

# AVL imports (assuming avl provides these helpers)
from avl import Env, Component, Driver, Monitor, Scoreboard, Agent, Sequence, Sequencer

class SimpleAdderDriver(Driver):
    async def _driver_send(self, transaction):
        # transaction is a dict with 'a' and 'b'
        self.log.debug(f"Driving transaction: {transaction}")
        self.bus.a.value = transaction['a']
        self.bus.b.value = transaction['b']


class SimpleAdderMonitor(Monitor):
    async def _monitor_recv(self):
        # capture output on every timestep
        while True:
            await Timer(1, units="ns")
            yield {'sum': int(self.bus.sum.value)}


class SimpleAdderTB(Env):
    def __init__(self, dut):
        super().__init__(dut)
        # create a port proxy (assuming avl.Component provides simple
        # signal-access wrapper)
        self.adder = Component(dut)

        # agents
        self.driver = SimpleAdderDriver(self.adder)
        self.monitor = SimpleAdderMonitor(self.adder)
        self.scoreboard = Scoreboard()

        # connect monitor output to scoreboard
        self.monitor.add_callback(self.scoreboard.write)

    async def run_test(self):
        # drive a couple of random transactions
        for a_val, b_val in [(1, 2), (5, 7), (255, 1)]:
            await self.driver.send({'a': a_val, 'b': b_val})
            await Timer(10, units="ns")

        # let monitor feed scoreboard for a short while
        await Timer(100, units="ns")


@cocotb.test()
async def avl_style_test(dut):
    tb = SimpleAdderTB(dut)
    await tb.run_test()
    # check results collected in scoreboard
    # simplistic assert for demonstration
    assert tb.scoreboard.transaction_count >= 3
    dut._log.info("AVL-style test completed")
