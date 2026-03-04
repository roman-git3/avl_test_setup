import cocotb
from cocotb.triggers import Timer
from avl import Component # Example AVL import

@cocotb.test()
async def my_first_test(dut):
    """Simple test to verify simulator connection"""
    dut._log.info("Hello from Cocotb + AVL!")
    
    # Initialize signals
    dut.a.value = 1
    dut.b.value = 2
    await Timer(10, units="ns")
    assert dut.sum.value == 3, f"Expected sum to be 3, got {dut.sum.value}"

    dut._log.info("Initial test finished successfully!")