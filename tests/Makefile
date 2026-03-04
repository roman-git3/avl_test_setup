# Simulator selection (can be overridden on command line)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Paths to your source files
VERILOG_SOURCES += $(PWD)/../hdl/my_design.sv
VERILOG_SOURCES += $(PWD)/../hdl/top_tb.sv

# The name of the top-level module in your Verilog
TOPLEVEL = top_tb

# The name of the Python test file (without .py)
# MODULE = test_my_design
COCOTB_TEST_MODULES = test_my_design

# Include Cocotb's standard build rules
include $(shell cocotb-config --makefiles)/Makefile.sim