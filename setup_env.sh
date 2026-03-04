#!/bin/bash
sudo apt update
sudo apt install -y build-essential iverilog verilator gtkwave
# Install uv if not present
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi
uv sync
