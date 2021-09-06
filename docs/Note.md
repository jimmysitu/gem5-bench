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



### Available Benchmark

SPEC CPU2006 includes 29 benchmarks, organized into 2 suites: an integer suite of 12 benchmarks, known as CINT2006; and a floating point suite of 17 benchmarks, known as CFP2006. 

* 400.perlbench
* 401.bzip2

* 403.gcc
* 410.bwaves
* 416.gamess
* 429.mcf
* 433.milc
* 434.zeusmp
* 435.gromacs
* 436.cactusADM
* 437.leslie3d
* 444.namd
* 445.gobmk
* 453.povray
* 454.calculix
* 456.hmmer
* 458.sjeng
* 459.GemsFDTD
* 462.libquantum
* 464.h264ref
* 465.tonto
* 470.lbm
* 471.omnetpp
* 473.astar
* 481.wrf
* 482.sphinx3
* 998.specrand
* 999.specrand

## Running SPEC CPU2017
