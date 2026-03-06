# cocotb + AVL Test Setup

Minimal working example of a [cocotb](https://www.cocotb.org/) + [AVL (Apheleia Verification Library)](https://pypi.org/project/avl-core/) testbench with a UVM-like structure, pytest-based regression, and GitHub Actions CI.

---

## DUT

**`hdl/my_design.sv`** — a simple 8-bit combinational adder:

```
inputs:  a [7:0], b [7:0]
output:  sum [8:0]  (= a + b)
```

**`hdl/top_tb.sv`** — Verilog wrapper instantiating the DUT as `u_simple_adder`, wired to `top_tb` ports. This is the elaboration top for Icarus. It also sets up VCD waveform dumping.

---

## Environment Setup

```bash
bash setup_env.sh
```

Installs system packages (`iverilog`, `verilator`, `gtkwave`, `build-essential`), installs `uv` if not present, and runs `uv sync` to create the Python virtual environment with all dependencies.

---

## Tests

### `tests/test_my_design.py`
Basic cocotb smoke test — drives `a=1, b=2`, waits 10 ns, asserts `sum == 3`.

### `tests/test_avl_simple.py`
AVL UVM-like testbench for the adder:

| Component | Class | Role |
|---|---|---|
| `AdderTransaction` | `Transaction` | Carries `a` (Uint8), `b` (Uint8), `sum` (Uint, 9-bit) |
| `SimpleAdderDriver` | `Driver` | Pops stimulus from `seq_item_port`, drives DUT signals |
| `SimpleAdderMonitor` | `Monitor` | Samples `sum` after each drive, writes to `item_export` |
| `SimpleAdderScoreboard` | `Scoreboard` | Predicts `sum = a + b`, compares against monitor observation |
| `SimpleAdderTB` | `Env` | Wires components, randomizes 15 transactions via `randomize()` |

The scoreboard holds the prediction logic — the env only generates randomized `(a, b)` stimulus. Fields `a` and `b` are excluded from comparison; only `sum` is checked.

---

## Running a Single Test

```bash
cd tests
uv run make COCOTB_TEST_MODULES=test_avl_simple
uv run make COCOTB_TEST_MODULES=test_my_design
```

---

## Regression

Run the full regression suite with pytest:

```bash
uv run pytest tests/test_runner.py -v
```

`tests/test_runner.py` uses `cocotb-test` to parametrize over all test modules. Add new test modules to the `@pytest.mark.parametrize` list there.

---

## Waveforms

Each simulation run writes a VCD file to `tests/dump.vcd`. Open it with GTKWave:

```bash
gtkwave tests/dump.vcd
```

Or use the [Surfer](https://surfer-project.org/) VSCode extension — point it at `tests/dump.vcd`.

---

## CI

GitHub Actions runs the full regression on every push and pull request to `master`/`main`.

**Workflow:** `.github/workflows/regression.yml`

Steps:
1. Checkout
2. Install `uv` (official `astral-sh/setup-uv` action)
3. `bash setup_env.sh` — installs system deps + `uv sync`
4. `uv run pytest tests/test_runner.py -v --tb=short`

`setup_env.sh` is the single source of truth for system dependencies — adding a new tool there is automatically picked up by CI.

---

## Project Structure

```
.
├── hdl/
│   ├── my_design.sv        # DUT: simple_adder
│   └── top_tb.sv           # Verilog elaboration top
├── tests/
│   ├── Makefile            # cocotb/Icarus build rules (single test runs)
│   ├── test_runner.py      # pytest regression entry point
│   ├── test_my_design.py   # smoke test
│   ├── test_avl_simple.py  # AVL UVM-like testbench
│   └── dump.vcd            # waveform output (after simulation)
├── .github/
│   └── workflows/
│       └── regression.yml  # CI pipeline
├── setup_env.sh            # developer environment setup
└── pyproject.toml          # Python project + dependencies
```
