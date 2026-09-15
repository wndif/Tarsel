# Tarsel2

Fault localization for **single-fault Verilog designs**.

Give Tarsel2 a faulty design, its testbench, and the output the correct design
should have produced. It runs one instrumented simulation per time window,
builds a binary line-coverage matrix from URG reports, and ranks every line by
six suspiciousness formulas.

## What it does

```
faulty RTL + testbench + golden output
    -> VCS compile with coverage instrumentation
    -> one full run, compared row by row against the golden output
    -> time windows derived from the divergence timeline
    -> one instrumented simulation + one URG report per window
    -> binary line-coverage matrix + pass/fail labels per window
    -> six suspiciousness formulas + optional EXAM score
```

The "test suite" is created by slicing a single simulation in time:
each window is one test, and a window is failing when the design's output
diverges from the golden output inside it.

## Requirements

- Python 3.8+
- **Synopsys VCS and URG** (`vcs`, `urg` on `PATH`) with a reachable licence.
  These are commercial tools and are not redistributed here.

Coverage acquisition cannot be replaced by Icarus Verilog: iverilog has no
line-coverage database equivalent to VCS `-cm` + URG.

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
tarsel2 check          # verifies vcs/urg are on PATH
```

## Use

Describe the design in a project yaml:

```yaml
project_name: updown_counter
project_dir: .
source_files:
  - updown_counter_buggy.v
testbench: updown_counter_tb.v
golden_output: golden_output.txt     # output of the correct version
output_filename: output.txt          # what the testbench writes
slice_strategy: onset                # or "uniform"
fault_lines:                         # optional; enables EXAM score
  - updown_counter_buggy_20
```

Then:

```bash
tarsel2 localize --config examples/updown_counter/tarsel2.yaml --work-dir work
```

Artifacts land in the work directory:

| File | Contents |
|---|---|
| `df_matrix_errors.csv` | raw coverage matrix plus the `error` row |
| `df_matrix_errors_purified.csv` | after module→file renaming and optimizers |
| `suspicious_values.csv` | aef/anf/aep/anp and all six scores per line |
| `ranking_D_star.csv` | full ranking by D_star |
| `exam_result.csv` | EXAM score per formula (needs `fault_lines`) |

### Testbench contract

The testbench must be **value-dumping**: write one CSV row per sample period
with a `time,<signals>` header, and never `$fatal`/`$finish` on mismatch. A
self-checking testbench aborts at the first mismatch and leaves no divergence
timeline to slice.

### Slicing strategies

- `onset` — sliding windows centred on divergence onsets, labelled by the
  divergence transition at the window end.
- `uniform` — fixed windows over the whole run, labelled failing when any
  divergence falls inside. Cleaner semantics; usually a better localization
  input.

### Optional optimizers

Enable with `optimizers: [canal, mss, span_merge]` (applied in order):

- `canal` — keep only windows up to the first failing one (in-time detection)
- `mss` — drop passing windows that cover the minimal suspicious set
- `span_merge` — add merged multi-window spans

## Docker

The image ships the tool and VCS runtime libraries. It contains no Synopsys
binary: mount your own volume.

```bash
docker volume create tarsel2_synopsys     # provision from your licensed install
docker build -f docker/Dockerfile -t tarsel2:local .

docker run --rm -v "$PWD:/data" \
    -v tarsel2_synopsys:/opt/synopsys:ro \
    -e LM_LICENSE_FILE=27000@<your-license-server> \
    tarsel2:local localize --config examples/updown_counter/tarsel2.yaml
```

See `docker/README.md` for the expected volume layout.

## Formulas

`Russel_Rao`, `OPTIMAL_P`, `GP02`, `GP03`, `GP19`, `D_star`. `OPTIMAL_P` is
`a11 - a01 / (a01 + a00 + 1)`.

## Citation

Tarsel2 implements time-aware fault localization for hardware design code. If
you use it in academic work, please cite:

> Jiang Wu, Zhuo Zhang, Deheng Yang, Xiankai Meng, Jiayu He, Xiaoguang Mao,
> Yan Lei. *Fault Localization for Hardware Design Code with Time-Aware Program
> Spectrum.* ICCD 2022: 537–544.

```bibtex
@inproceedings{wu2022faultlocalization,
  author    = {Wu, Jiang and Zhang, Zhuo and Yang, Deheng and Meng, Xiankai and
               He, Jiayu and Mao, Xiaoguang and Lei, Yan},
  title     = {Fault Localization for Hardware Design Code with Time-Aware
               Program Spectrum},
  booktitle = {2022 IEEE 40th International Conference on Computer Design (ICCD)},
  pages     = {537--544},
  year      = {2022}
}
```

## Licensing

MIT. See `THIRD_PARTY_NOTICES.md` for third-party software notices.
