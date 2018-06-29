# gem5 Bench
A wrapper for simulation with gem5

## gem5 Basic
- Getting start with [Learning gem5](http://learning.gem5.org/)

## Install Dependencies Packages
```bash
sudo apt install build-essential git m4 scons zlib1g zlib1g-dev libprotobuf-dev protobuf-compiler libprotoc-dev libgoogle-perftools-dev python-dev python
```
Install KVM, following instruction on this [page](https://help.ubuntu.com/community/KVM/Installation)

Install Qemu, for creating gem5 full system image
```bash
sudo apt-get install qemu-kvm qemu virt-manager virt-viewer libvirt-bin virtinst kpartx
```

Install gcc for ARM if want to build linux kernel for Aarch64
```
sudo apt-get install gcc-aarch64-linux-gnu device-tree-compiler
```

## Build SPEC2006 for gem5 SE mode
First, build spec2006 on native machine
```bash
make BUILD_SPEC2006_$(ISA)
```
Second, run spec2006 on native machine for gem5 do not implement mkdir syscall, some tmp/result dir need to be setup firstly
```bash
make RUN_SPEC2006_$(ISA)
```

## Run SPEC2006 on gem5 SE mode
First, list all available benchmark and workload
```bash
make list-wrkld
```
Run benchmark case
```bash
make $(benchname) ISA=$(ISA) WRKLD=$(WORKLOAD)
```

## Build Linux Kernel for gem5 Full System Mode
Install Ubuntu 16.04 to disk image for gem5 full system mode
```bash
make build_img_x86
```

## TODO
- Add Full system image making flow for x86
- Add Full system image making flow for ARM
- Add install spec2006 flow to system image
- Add McPAT flow for power analysis



