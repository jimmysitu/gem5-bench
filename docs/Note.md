# gem5-bench Notes

## Running SPEC CPU2006

### Install SPEC CPU2006

Mount the ISO file and install SPEC CPU2006 with

```bash
sudo mount -t iso9660 -o ro,exec <path_to_spec_iso> /mnt
cd /mnt
./install.sh -d <path_to_install>
```

### Build SPEC CPU2006

Build only cmd,

```bash
runspec --action build --config <cfg_file> <benchmark>
```

`runspec` build action will change cfg file, so it is better to copy a new cfg file for each build.

### Run SPEC CPU2006

Run only cmd,

```bash
runspec --noreportable --nobuild --config <cfg_file> <benchmark>
```

**--nobuild**: is added for prebuilt binaries should be used

**--fake**: dry run

#### Tips: Get Final Run Command

After build and setup SPEC CPU2006 enviroment, one can get the final command with `specinvoke`. This command is useful when build and run are on different machines (e.g x86 and gem5)

For example,

```bash
go 400.perlbench run; #Go to run dir
specinvoke -n
```

And return,

```bash
# specinvoke r6392
#  Invoked as: specinvoke -n
# timer ticks over every 1000 ns
# Use another -n on the command line to see chdir commands and env dump
# Starting run for copy #0
../run_base_ref_gem5-x86.0000/perlbench_base.gem5-x86 -I./lib checkspam.pl 2500 5 25 11 150 1 1 1 1 > checkspam.2500.5.25.11.150.1.1.1.1.out 2>> checkspam.2500.5.25.11.150.1.1.1.1.err
# Starting run for copy #0
../run_base_ref_gem5-x86.0000/perlbench_base.gem5-x86 -I./lib diffmail.pl 4 800 10 17 19 300 > diffmail.4.800.10.17.19.300.out 2>> diffmail.4.800.10.17.19.300.err
# Starting run for copy #0
../run_base_ref_gem5-x86.0000/perlbench_base.gem5-x86 -I./lib splitmail.pl 1600 12 26 16 4500 > splitmail.1600.12.26.16.4500.out 2>> splitmail.1600.12.26.16.4500.err
```



### 



### Metrics

For CPU2006, SPEC has chosen to allow two types of compilation:

- The **base** metrics (e.g. SPECint_base2006) are required for all reported results and have stricter guidelines for compilation. For example, the same flags must be used in the same order for all benchmarks of a given language. This is the point closer to those who might prefer a relatively simple build process.
- The **peak** metrics (e.g. SPECint2006) are optional and have less strict requirements. For example, different compiler options may be used on each benchmark, and feedback-directed optimization is allowed. This point is closer to those who may be willing to invest more time and effort in development of build procedures.

The **SPECspeed metrics** (e.g., SPECint2006) are used for comparing the ability of a computer to complete single tasks.

- **SPECspeed metrics:**
  - **SPECint2006**: The geometric mean of twelve normalized ratios - one for each integer benchmark - when the benchmarks are compiled with [peak](https://www.spec.org/cpu2006/Docs/readme1st.html#Q14) tuning.
  - **SPECint_base2006**: The geometric mean of twelve normalized ratios when the benchmarks are compiled with [base](https://www.spec.org/cpu2006/Docs/readme1st.html#Q14) tuning.
  - **SPECfp2006**: The geometric mean of seventeen normalized ratios - one for each floating point benchmark - when compiled with [peak](https://www.spec.org/cpu2006/Docs/readme1st.html#Q14) tuning.
  - **SPECfp_base2006**: The geometric mean of seventeen normalized ratios when the benchmarks are compiled with [base](https://www.spec.org/cpu2006/Docs/readme1st.html#Q14) tuning.

The **SPECrate metrics** (e.g., SPECint_rate2006) measure the throughput or rate of a machine carrying out a number of tasks.

- **SPECrate metrics:**
  - **SPECint_rate2006**: The geometric mean of twelve normalized [throughput](https://www.spec.org/cpu2006/Docs/readme1st.html#Q15) ratios when the benchmarks are compiled with peak tuning.
  - **SPECint_rate_base2006**: The geometric mean of twelve normalized throughput ratios when the benchmarks are compiled with base tuning.
  - **SPECfp_rate2006**: The geometric mean of seventeen normalized [throughput](https://www.spec.org/cpu2006/Docs/readme1st.html#Q15) ratios when the benchmarks are compiled with peak tuning.
  - **SPECfp_rate_base2006**: The geometric mean of seventeen normalized throughput ratios when the benchmarks are compiled with base tuning.



### Available Benchmark

#### CINT2006

| Item                                                         | Language | Description                    |
| ------------------------------------------------------------ | -------- | ------------------------------ |
| [400.perlbench](http://www.spec.org/auto/cpu2006/Docs/400.perlbench.html) | C        | PERL Programming Language      |
| [401.bzip2](http://www.spec.org/auto/cpu2006/Docs/401.bzip2.html) | C        | Compression                    |
| [403.gcc](http://www.spec.org/auto/cpu2006/Docs/403.gcc.html) | C        | C Compiler                     |
| [429.mcf](http://www.spec.org/auto/cpu2006/Docs/429.mcf.html) | C        | Combinatorial Optimization     |
| [445.gobmk](http://www.spec.org/auto/cpu2006/Docs/445.gobmk.html) | C        | Artificial Intelligence: go    |
| [456.hmmer](http://www.spec.org/auto/cpu2006/Docs/456.hmmer.html) | C        | Search Gene Sequence           |
| [458.sjeng](http://www.spec.org/auto/cpu2006/Docs/458.sjeng.html) | C        | Artificial Intelligence: chess |
| [462.libquantum](http://www.spec.org/auto/cpu2006/Docs/462.libquantum.html) | C        | Physics: Quantum Computing     |
| [464.h264ref](http://www.spec.org/auto/cpu2006/Docs/464.h264ref.html) | C        | Video Compression              |
| [471.omnetpp](http://www.spec.org/auto/cpu2006/Docs/471.omnetpp.html) | C++      | Discrete Event Simulation      |
| [473.astar](http://www.spec.org/auto/cpu2006/Docs/473.astar.html) | C++      | Path-finding Algorithms        |
| [483.xalancbmk](http://www.spec.org/auto/cpu2006/Docs/483.xalancbmk.html) | C++      | XML Processing                 |

#### CFP2006

| Item                                                         | Language  | Description                      |
| ------------------------------------------------------------ | --------- | -------------------------------- |
| [410.bwaves](http://www.spec.org/auto/cpu2006/Docs/410.bwaves.html) | Fortran   | Fluid Dynamics                   |
| [416.gamess](http://www.spec.org/auto/cpu2006/Docs/416.gamess.html) | Fortran   | Quantum Chemistry                |
| [433.milc](http://www.spec.org/auto/cpu2006/Docs/433.milc.html) | C         | Physics: Quantum Chromodynamics  |
| [434.zeusmp](http://www.spec.org/auto/cpu2006/Docs/434.zeusmp.html) | Fortran   | Physics/CFD                      |
| [435.gromacs](http://www.spec.org/auto/cpu2006/Docs/435.gromacs.html) | C/Fortran | Biochemistry/Molecular Dynamics  |
| [436.cactusADM](http://www.spec.org/auto/cpu2006/Docs/436.cactusADM.html) | C/Fortran | Physics/General Relativity       |
| [437.leslie3d](http://www.spec.org/auto/cpu2006/Docs/437.leslie3d.html) | Fortran   | Fluid Dynamics                   |
| [444.namd](http://www.spec.org/auto/cpu2006/Docs/444.namd.html) | C++       | Biology/Molecular Dynamics       |
| [447.dealII](http://www.spec.org/auto/cpu2006/Docs/447.dealII.html) | C++       | Finite Element Analysis          |
| [450.soplex](http://www.spec.org/auto/cpu2006/Docs/450.soplex.html) | C++       | Linear Programming, Optimization |
| [453.povray](http://www.spec.org/auto/cpu2006/Docs/453.povray.html) | C++       | Image Ray-tracing                |
| [454.calculix](http://www.spec.org/auto/cpu2006/Docs/454.calculix.html) | C/Fortran | Structural Mechanics             |
| [459.GemsFDTD](http://www.spec.org/auto/cpu2006/Docs/459.GemsFDTD.html) | Fortran   | Computational Electromagnetics   |
| [465.tonto](http://www.spec.org/auto/cpu2006/Docs/465.tonto.html) | Fortran   | Quantum Chemistry                |
| [470.lbm](http://www.spec.org/auto/cpu2006/Docs/470.lbm.html) | C         | Fluid Dynamics                   |
| [481.wrf](http://www.spec.org/auto/cpu2006/Docs/481.wrf.html) | C/Fortran | Weather Prediction               |
| [482.sphinx3](http://www.spec.org/auto/cpu2006/Docs/482.sphinx3.html) | C         | Speech recognition               |

## Running SPEC CPU2017
