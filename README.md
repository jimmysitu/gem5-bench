# gem5 Bench
A wrapper for simulation with gem5

## gem5 Basic
- Getting start with [Learning gem5](http://learning.gem5.org/)

## Host machine requirements
- At least 32G DRAM for full system mode with spec2006/spec2017 installed

### Install Dependencies Packages
```bash
sudo apt install build-essential git m4 scons zlib1g zlib1g-dev libprotobuf-dev protobuf-compiler libprotoc-dev libgoogle-perftools-dev python-dev python gcc-multilib g++multilib
```

### Install QEMU & KVM

Following instruction on this [page](https://help.ubuntu.com/community/KVM/Installation). Add user to group kvm

```bash
sudo adduser `whoami` kvm
````
Reboot to make this setting works

Install QEMU, for creating gem5 full system image
```bash
sudo apt-get install qemu-kvm qemu virt-manager virt-viewer libvirt-bin virtinst kpartx
```


Install gcc for ARM if want to build linux kernel for Aarch64
```
sudo apt-get install gcc-aarch64-linux-gnu device-tree-compiler
```

### Install Docker

Docker, which is used to run mongoDB. Following instruction on this [page](https://docs.docker.com/engine/install/ubuntu/). Add user to group docker

```bash
sudo usermod -aG docker ${USER}
```

To apply the new group membership, log out of the server and back in, or type the following:

```bash
su - ${USER}
```

Test docker

```bash
docker run hello-world
```

### Install Packer

Packer, which is used to make full system disk image for gem5. Following instruction on this [page](https://www.packer.io/downloads)

```bash
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install packer
```

### Install gem5art

gem5-bench need gem5art to run and reproduce experiment results. 

```bash
pip install gem5art-artifact gem5art-run gem5art-tasks
```



## Build SPEC2006 for gem5 SE mode

First, build spec2006 on native machine
```bash
make build_spec2006_$(ISA)
```
Second, run spec2006 once on native machine since gem5 do not implement `mkdir` syscall, some tmp/result dir need to be setup firstly
```bash
make run_spec2006_$(ISA)
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

Build Linux kernel, you can define you kernel in linux_configs/config-\<ISA>-<KERNEL_VERSION>
```bash
make build_kernel_X86
```

Install Ubuntu 16.04 to disk image for gem5 full system mode
```bash
make build_img_x86
```

Install tools and benchmark to disk image
```bash
make install_spec_x86
```
If your host kernel is different from the guest, recompile of spec2006 may need. Try to recompile it on qemu
```bash
make run_qemu_x86
```
Once logined, compile the benchmark with this command
```bash
export M5_CPU2006=<path_to_CPU2006>
make setup_spec2006_X86
```
Try run benchmark on qemu, and make sure benchmark exists without error
```bash
sh ./m5tools/400.xxxxxx.sh
```

## Run Benchmark on gem5 with Full System Mode

```bash
make run_gem5_x86 CMD=./m5tools/<benchmark>.sh
```
Log of benchmark will be wrote to ./m5out/*.out

## TODO
- Add McPAT flow for power analysis
  - xml templete for McPAT
  - Configure more detail O3CPU on gem5 in fs_run.py
  - Add power analysis flow in Makefile
- Add Full system image making flow for ARM/RISC-V
- Output redirect not work in SE mode
- Auto login in tty mode, which may help gem5 FS mode run faster?

## Trouble Shooting
### gem5 is killed by system

Double confirm this issue by
```bash
grep -i 'killed process' /var/log/kern.log
```

Workaround
```bash
sudo su
echo 1 > /proc/sys/vm/overcommit_memory
```
Documentation [here](https://www.kernel.org/doc/Documentation/sysctl/vm.txt)





