# This makefile include most useful target of Gem5

ISO_URL  = http://releases.ubuntu.com/xenial
ISO_NAME = ubuntu-16.04.4-server-amd64.iso

ISAs := X86 ARM RISCV
exts := opt prof perf debug

BUILD_SPECs = $(foreach ISA, $(ISAs), build_spec2006_$(ISA))
SETUP_SPECs = $(foreach ISA, $(ISAs), setup_spec2006_$(ISA))
RUN_SPECs = $(foreach ISA, $(ISAs), run_spec2006_$(ISA))
CLEAN_SPECs = $(foreach ISA, $(ISAs), clean_spec2006_$(ISA))

GEM5_TARGETs = $(foreach ISA, $(ISAs), $(foreach ext, $(exts),  gem5/build/$(ISA)/gem5.$(ext)))
KERNEL_TARGETs = $(foreach ISA, $(ISAs), build_kernel_$(ISA))


.PHONY: get-iso check-env check-isa check-wrkld $(BUILD_SPECs) $(SETUP_SPECs) $(RUN_SPECs) $(CLEAN_SPECs)

get-iso:
	wget $(ISO_URL)/$(ISO_NAME)

# Check M5_CPU2006, it should point to SPEC2006 install dir
check-env:
ifndef M5_CPU2006
	$(error M5_CPU2006 is undefined)
endif

check-isa:
ifndef ISA
	$(error ISA is undefined)
endif

check-wrkld:
ifndef WRKLD
	$(error WRKLD is undefined, try list-wrkld)
endif

list-wrkld:
	python2 configs/cpu2006.py --list | grep workloads

gen-spec2006-cmd:
	python2 configs/cpu2006.py --generate

# Build SPEC2006 for gem5
$(BUILD_SPECs): check-env
	cp ${PWD}/spec2006_configs/gem5-$(subst build_spec2006_,,$@).cfg ${PWD}/spec2006_configs/gem5-$(subst build_spec2006_,,$@).bld.cfg; \
	cd ${M5_CPU2006}; \
	. ./shrc; \
	runspec --action=build --tuning=base --noreportable --config ${PWD}/spec2006_configs/gem5-$(subst build_spec2006_,,$@).bld.cfg int; \
	runspec --action=build --tuning=base --noreportable --config ${PWD}/spec2006_configs/gem5-$(subst build_spec2006_,,$@).bld.cfg fp;
	@echo "$(@) build done"

# Setup the run dir before gem5 simulation
$(SETUP_SPECs): check-env
	cp ${PWD}/spec2006_configs/gem5-$(subst setup_spec2006_,,$@).cfg ${PWD}/spec2006_configs/gem5-$(subst setup_spec2006_,,$@).bld.cfg; \
	cd ${M5_CPU2006}; \
	. ./shrc; \
	runspec --action=setup --tuning=base -i ref -n 1 --noreportable --config ${PWD}/spec2006_configs/gem5-$(subst setup_spec2006_,,$@).bld.cfg int; \
	runspec --action=setup --tuning=base -i ref -n 1 --noreportable --config ${PWD}/spec2006_configs/gem5-$(subst setup_spec2006_,,$@).bld.cfg fp; 
	@echo "$(@) done"

# Try run on native machine before gem5 simulation
$(RUN_SPECs): check-env
	cd ${M5_CPU2006}; \
	. ./shrc; \
	runspec --action=run --tuning=base -i ref -n 1 --noreportable --config ${PWD}/spec2006_configs/gem5-$(subst run_spec2006_,,$@).bld.cfg int; \
	runspec --action=run --tuning=base -i ref -n 1 --noreportable --config ${PWD}/spec2006_configs/gem5-$(subst run_spec2006_,,$@).bld.cfg fp;
	@echo "$(@) done"

# Clean SPEC2006 for gem5
$(CLEAN_SPECs): check-env
	cd ${M5_CPU2006}; \
	. ./shrc; \
	runspec --action=clean --config ${PWD}/spec2006_configs/gem5-$(subst clean_spec2006_,,$@).bld.cfg int; \
	runspec --action=clean --config ${PWD}/spec2006_configs/gem5-$(subst clean_spec2006_,,$@).bld.cfg fp; \
	rm ${PWD}/spec2006_configs/gem5-$(subst clean_spec2006_,,$@).bld.cfg;
	@echo "$(@) done"

# Build gem5
$(GEM5_TARGETs): gem5/src
	cd gem5; \
	scons -j `nproc` $(subst gem5/,,$@)

build_gem5_all: $(GEM5_TARGETs)
	@echo "Build All Targets Done"


# TODO: Long run for this simulation, slurm should be used
# SE Mode
BENCHs = perlbench bzip2 gcc bwaves gamess mcf milc zeusmp gromacs cactusADM leslie3d namd gobmk dealII soplex povray calculix hmmer sjeng GemsFDTD libquantum h264ref tonto lbm omnetpp astar wrf sphinx3 xalancbmk specrand_int specrand_fp

$(BENCHs): check-isa check-wrkld
	./gem5/build/$(ISA)/gem5.opt configs/se_cpu2006.py \
		--mem-size="2048MB" --bench=$@ --spec-workload=$(WRKLD) \
		--output=$@_$(WRKLD).out --errout=$@_$(WRKLD).err


# Build linux kernel for gem5
$(KERNEL_TARGETs):
	cp linux_configs/config-$(subst build_kernel_,,$@) linux/.config
	cd linux; make -j `nproc`
	@echo "$(@) done"

# Build Full System disk
build_img_x86:
	@echo "Automatic install ubuntu to ubuntu-1604.X86.img"
ifeq (,$(wildcard ./ubuntu-1604.X86.img)) 
	@echo "Create image file"
	qemu-img create ubuntu-1604.X86.img 8G
	cp linux_configs/preseed-X86.cfg preseed.cfg
	sudo virt-install \
		--connect qemu:///system \
		--name gem5-ubuntu \
		--ram 2048 \
		--network network=default,model=virtio \
		--disk path=${PWD}/ubuntu-1604.X86.img,size=8,bus=virtio,sparse=false,format=raw \
		--location ubuntu-16.04.4-server-amd64.iso \
		--initrd-inject=${PWD}/preseed.cfg \
		--extra-args="locale=en_GB.UTF-8 console-setup/ask_detect=false keyboard-configuration/layoutcode=hu console=ttyS0 file=/preseed.cfg" \
		--virt-type kvm \
		--noreboot \
		--nographics
	sudo chown `whoami` ubuntu-1604.X86.img

else
	@echo "Image file ubuntu-1604.X86.img already exist, please remove it manually first"
endif

destroy_img_x86:
	-virsh destroy gem5-ubuntu
	-virsh undefine gem5-ubuntu --remove-all-storage

# Run qemu to check kernel
run_qemu_x86:
	qemu-system-x86_64 -nographic -hda ubuntu-1604.X86.img \
		-enable-kvm \
		-m 2048 \
		-kernel linux/arch/x86_64/boot/bzImage -append "root=/dev/hda1 console=ttyS0"

run_gem5_x86:
	./gem5/build/X86/gem5.opt configs/run.py --script=$(CMD)

# Build util for full system
build_util_x86:
	cd gem5/util/m5; \
	make -f Makefile.x86 CC='gcc -no-pie'

build_util_aarch64:
	cd gem5/util/m5; \
	make -f Makefile.aarch64

# Install tools to full system disk
install_tools_x86: build_util_x86
	./m5tools/render_gem5init.py
	chmod +x ./m5tools/gem5init
	sudo kpartx -av ubuntu-1604.X86.img
	@sleep 1
	sudo mount /dev/mapper/loop0p1 /mnt
	sudo cp gem5/util/m5/m5 /mnt/sbin/.
	sudo cp m5tools/gem5init /mnt/sbin/.
	sudo cp m5tools/gem5.service /mnt/lib/systemd/system/.
	-cd /mnt/etc/systemd/system/default.target.wants; \
		sudo ln -s /lib/systemd/system/gem5.service
	-sudo rm /mnt/home/gem5/gem5init.log
	sudo umount /mnt
	sudo kpartx -dv ubuntu-1604.X86.img

install_spec_x86: install_tools_x86 setup_spec2006_X86 gen-spec2006-cmd
	make clean_spec2006_X86
	sudo kpartx -av ubuntu-1604.X86.img
	@sleep 1
	sudo mount /dev/mapper/loop0p1 /mnt
	sudo cp --parents -r ${M5_CPU2006} /mnt/.
	sudo chown 1010 /mnt/$(M5_CPU2006) -R
	sudo chgrp 1010 /mnt/$(M5_CPU2006) -R
	sudo cp Makefile /mnt/home/gem5/.
	sudo cp -r spec2006_configs /mnt/home/gem5/.
	sudo cp -r m5tools /mnt/home/gem5/.
	sudo chown 1010 /mnt/home/gem5/* -R
	sudo chgrp 1010 /mnt/home/gem5/* -R
	sudo umount /mnt
	sudo kpartx -dv ubuntu-1604.X86.img
	@echo "SPEC2006 installed to image"
	@echo "Recompile may need if guest kernel is different from host"

# Debug commands
mount_img_x86:
	sudo kpartx -av ubuntu-1604.X86.img
	@sleep 1
	sudo mount /dev/mapper/loop0p1 /mnt

umount_img_x86:
	sudo umount /mnt
	sudo kpartx -dv ubuntu-1604.X86.img

term:
	./gem5/util/term/m5term localhost 3456

