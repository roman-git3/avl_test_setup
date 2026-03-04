# Simulator selection (can be overridden on command line)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Paths to your source files
VERILOG_SOURCES += $(PWD)/../hdl/my_design.sv

# The name of the top-level module in your Verilog
TOPLEVEL = simple_adder

# The name of the Python test file (without .py)
# MODULE = test_my_design
COCOTB_TEST_MODULES = test_my_design

# Include Cocotb's standard build rules
include $(shell cocotb-config --makefiles)/Makefile.sim