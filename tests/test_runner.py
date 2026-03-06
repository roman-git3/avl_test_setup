from pathlib import Path

import pytest
from cocotb_test.simulator import run

PROJ_ROOT = Path(__file__).parent.parent
SOURCES = [
    str(PROJ_ROOT / "hdl" / "my_design.sv"),
    str(PROJ_ROOT / "hdl" / "top_tb.sv"),
]
SIM_BUILD = str(Path(__file__).parent / "sim_build")
TESTS_DIR = str(Path(__file__).parent)


@pytest.mark.parametrize("module", [
    "test_my_design",
    "test_avl_simple",
])
def test_regression(module):
    run(
        verilog_sources=SOURCES,
        toplevel="top_tb",
        toplevel_lang="verilog",
        module=module,
        sim_build=SIM_BUILD,
        timescale="1ns/1ps",
        extra_env={"PYTHONPATH": TESTS_DIR},
    )
