# gem5-bench Note

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

Which returns,

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

### Clean Build/Run Directories

```bash
runspec --atction clean -c <cfg_file> <benchmark>
```

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

The former runspec utility is renamed runcpu in SPEC CPU 2017.  [[Why?](https://www.spec.org/cpu2017/Docs/runspec.html)]

### Install SPEC CPU2017

Mount the ISO file and install SPEC CPU2006 with

```bash
sudo mount -t iso9660 -o ro,exec,loop <path_to_spec_iso> /mnt
cd /mnt
./install.sh -d <path_to_install>
```

### Build SPEC CPU2017

Build only cmd,

```bash
runcpu --action build --config <cfg_file> <benchmark>
```

**--define build_ncpus=`` `nproc` ``**, parallel build with n CPUs

**--define gcc_dir="/usr"**, set gcc tool set directory

`runcpu` build action will change cfg file, so it is better to copy a new cfg file for each build.



### Run SPEC CPU2017



### Available Benchmark

SPEC CPU 2017 has 43 benchmarks, organized into 4 suites:

```text
 SPECrate 2017 Integer            SPECspeed 2017 Integer
 SPECrate 2017 Floating Point     SPECspeed 2017 Floating Point
```

Benchmark pairs shown as:

```text
 5nn.benchmark_r / 6nn.benchmark_s
```

|                    SPECrate®2017 Integer                     |                    SPECspeed®2017 Integer                    | Language[[1\]](https://www.spec.org/cpu2017/Docs/index.html#linkNote) | KLOC[[2\]](https://www.spec.org/cpu2017/Docs/index.html#klocNote) | Application Area                                             |
| :----------------------------------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: | -----------------------------------------------------------: | :----------------------------------------------------------- |
| [500.perlbench_r](https://www.spec.org/cpu2017/Docs/benchmarks/500.perlbench_r.html) | [600.perlbench_s](https://www.spec.org/cpu2017/Docs/benchmarks/600.perlbench_s.html) |                              C                               |                                                          362 | Perl interpreter                                             |
| [502.gcc_r](https://www.spec.org/cpu2017/Docs/benchmarks/502.gcc_r.html) | [602.gcc_s](https://www.spec.org/cpu2017/Docs/benchmarks/602.gcc_s.html) |                              C                               |                                                        1,304 | GNU C compiler                                               |
| [505.mcf_r](https://www.spec.org/cpu2017/Docs/benchmarks/505.mcf_r.html) | [605.mcf_s](https://www.spec.org/cpu2017/Docs/benchmarks/605.mcf_s.html) |                              C                               |                                                            3 | Route planning                                               |
| [520.omnetpp_r](https://www.spec.org/cpu2017/Docs/benchmarks/520.omnetpp_r.html) | [620.omnetpp_s](https://www.spec.org/cpu2017/Docs/benchmarks/620.omnetpp_s.html) |                             C++                              |                                                          134 | Discrete Event simulation - computer network                 |
| [523.xalancbmk_r](https://www.spec.org/cpu2017/Docs/benchmarks/523.xalancbmk_r.html) | [623.xalancbmk_s](https://www.spec.org/cpu2017/Docs/benchmarks/623.xalancbmk_s.html) |                             C++                              |                                                          520 | XML to HTML conversion via XSLT                              |
| [525.x264_r](https://www.spec.org/cpu2017/Docs/benchmarks/525.x264_r.html) | [625.x264_s](https://www.spec.org/cpu2017/Docs/benchmarks/625.x264_s.html) |                              C                               |                                                           96 | Video compression                                            |
| [531.deepsjeng_r](https://www.spec.org/cpu2017/Docs/benchmarks/531.deepsjeng_r.html) | [631.deepsjeng_s](https://www.spec.org/cpu2017/Docs/benchmarks/631.deepsjeng_s.html) |                             C++                              |                                                           10 | Artificial Intelligence: alpha-beta tree search (Chess)      |
| [541.leela_r](https://www.spec.org/cpu2017/Docs/benchmarks/541.leela_r.html) | [641.leela_s](https://www.spec.org/cpu2017/Docs/benchmarks/641.leela_s.html) |                             C++                              |                                                           21 | Artificial Intelligence: Monte Carlo tree search (Go)        |
| [548.exchange2_r](https://www.spec.org/cpu2017/Docs/benchmarks/548.exchange2_r.html) | [648.exchange2_s](https://www.spec.org/cpu2017/Docs/benchmarks/648.exchange2_s.html) |                           Fortran                            |                                                            1 | Artificial Intelligence: recursive solution generator (Sudoku) |
| [557.xz_r](https://www.spec.org/cpu2017/Docs/benchmarks/557.xz_r.html) | [657.xz_s](https://www.spec.org/cpu2017/Docs/benchmarks/657.xz_s.html) |                              C                               |                                                           33 | General data compression                                     |

|                 SPECrate®2017 Floating Point                 |                SPECspeed®2017 Floating Point                 | Language[[1\]](https://www.spec.org/cpu2017/Docs/index.html#linkNote) | KLOC[[2\]](https://www.spec.org/cpu2017/Docs/index.html#klocNote) | Application Area                                            |
| :----------------------------------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: | -----------------------------------------------------------: | :---------------------------------------------------------- |
| [503.bwaves_r](https://www.spec.org/cpu2017/Docs/benchmarks/503.bwaves_r.html) | [603.bwaves_s](https://www.spec.org/cpu2017/Docs/benchmarks/603.bwaves_s.html) |                           Fortran                            |                                                            1 | Explosion modeling                                          |
| [507.cactuBSSN_r](https://www.spec.org/cpu2017/Docs/benchmarks/507.cactuBSSN_r.html) | [607.cactuBSSN_s](https://www.spec.org/cpu2017/Docs/benchmarks/607.cactuBSSN_s.html) |                       C++, C, Fortran                        |                                                          257 | Physics: relativity                                         |
| [508.namd_r](https://www.spec.org/cpu2017/Docs/benchmarks/508.namd_r.html) |                                                              |                             C++                              |                                                            8 | Molecular dynamics                                          |
| [510.parest_r](https://www.spec.org/cpu2017/Docs/benchmarks/510.parest_r.html) |                                                              |                             C++                              |                                                          427 | Biomedical imaging: optical tomography with finite elements |
| [511.povray_r](https://www.spec.org/cpu2017/Docs/benchmarks/511.povray_r.html) |                                                              |                            C++, C                            |                                                          170 | Ray tracing                                                 |
| [519.lbm_r](https://www.spec.org/cpu2017/Docs/benchmarks/519.lbm_r.html) | [619.lbm_s](https://www.spec.org/cpu2017/Docs/benchmarks/619.lbm_s.html) |                              C                               |                                                            1 | Fluid dynamics                                              |
| [521.wrf_r](https://www.spec.org/cpu2017/Docs/benchmarks/521.wrf_r.html) | [621.wrf_s](https://www.spec.org/cpu2017/Docs/benchmarks/621.wrf_s.html) |                          Fortran, C                          |                                                          991 | Weather forecasting                                         |
| [526.blender_r](https://www.spec.org/cpu2017/Docs/benchmarks/526.blender_r.html) |                                                              |                            C++, C                            |                                                        1,577 | 3D rendering and animation                                  |
| [527.cam4_r](https://www.spec.org/cpu2017/Docs/benchmarks/527.cam4_r.html) | [627.cam4_s](https://www.spec.org/cpu2017/Docs/benchmarks/627.cam4_s.html) |                          Fortran, C                          |                                                          407 | Atmosphere modeling                                         |
|                                                              | [628.pop2_s](https://www.spec.org/cpu2017/Docs/benchmarks/628.pop2_s.html) |                          Fortran, C                          |                                                          338 | Wide-scale ocean modeling (climate level)                   |
| [538.imagick_r](https://www.spec.org/cpu2017/Docs/benchmarks/538.imagick_r.html) | [638.imagick_s](https://www.spec.org/cpu2017/Docs/benchmarks/638.imagick_s.html) |                              C                               |                                                          259 | Image manipulation                                          |
| [544.nab_r](https://www.spec.org/cpu2017/Docs/benchmarks/544.nab_r.html) | [644.nab_s](https://www.spec.org/cpu2017/Docs/benchmarks/644.nab_s.html) |                              C                               |                                                           24 | Molecular dynamics                                          |
| [549.fotonik3d_r](https://www.spec.org/cpu2017/Docs/benchmarks/549.fotonik3d_r.html) | [649.fotonik3d_s](https://www.spec.org/cpu2017/Docs/benchmarks/649.fotonik3d_s.html) |                           Fortran                            |                                                           14 | Computational Electromagnetics                              |
| [554.roms_r](https://www.spec.org/cpu2017/Docs/benchmarks/554.roms_r.html) | [654.roms_s](https://www.spec.org/cpu2017/Docs/benchmarks/654.roms_s.html) |                           Fortran                            |                                                          210 | Regional ocean modeling                                     |
