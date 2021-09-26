# This makefile include most useful target of gem5

ISAs := X86 ARM RISCV
exts := opt prof perf debug

BUILD_SPECs = $(foreach ISA, $(ISAs), build_spec2006_$(ISA))
SETUP_SPECs = $(foreach ISA, $(ISAs), setup_spec2006_$(ISA))
RUN_SPECs = $(foreach ISA, $(ISAs), run_spec2006_$(ISA))
CLEAN_SPECs = $(foreach ISA, $(ISAs), clean_spec2006_$(ISA))

GEM5_TARGETs = $(foreach ISA, $(ISAs), $(foreach ext, $(exts),  gem5/build/$(ISA)/gem5.$(ext)))
KERNEL_TARGETs = $(foreach ISA, $(ISAs), build_kernel_$(ISA))
IMAGE_TARGETs = $(foreach ISA, $(ISAs), build_img_$(ISA))
QEMU_TARGETs = $(foreach ISA, $(ISAs), run_qemu_$(ISA))


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

WRKLD ?= ''
check-wrkld:
ifndef WRKLD
	$(error WRKLD is undefined, try list-wrkld)
endif

list-wrkld:
	python3 configs/cpu2006.py --list | grep workloads

gen-spec2006-cmd:
	python3 configs/cpu2006.py --generate

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


# Run SPEC_CPU2006 in SE Mode
BENCHs = perlbench bzip2 gcc bwaves gamess mcf milc zeusmp gromacs cactusADM leslie3d namd gobmk dealII soplex povray calculix hmmer sjeng GemsFDTD libquantum h264ref tonto lbm omnetpp astar wrf sphinx3 xalancbmk specrand_int specrand_fp

$(BENCHs): check-isa check-wrkld
	./gem5/build/$(ISA)/gem5.opt configs/se_cpu2006.py \
		--mem-size="2048MB" --bench=$@ --spec-workload=$(WRKLD) \
		--output=$@_$(WRKLD).out --errout=$@_$(WRKLD).err


# Build linux kernel for gem5
KERNEL_VERSION ?= 5.4.49
$(KERNEL_TARGETs): ISA = $(subst build_kernel_,,$@)
$(KERNEL_TARGETs):
	cd linux; git checkout v$(KERNEL_VERSION)
	cp linux_configs/config-$(ISA)-$(KERNEL_VERSION) linux/.config
	cd linux; make -j `nproc`
	cd linux; cp vmlinux vmlinux-$(ISA)-$(KERNEL_VERSION)
	@echo "$(@) $(KERNEL_VERSION) done"

# Build Full System disk
UBUNTU_VERSION ?= 18.04
$(IMAGE_TARGETs): ISA = $(subst build_img_,,$@)
$(IMAGE_TARGETs):
	@echo "Building disk image with Ubuntu $(UBUNTU_VERSION)"
	packer validate packer_configs/ubuntu-$(ISA)-$(UBUNTU_VERSION).json
	packer build packer_configs/ubuntu-$(ISA)-$(UBUNTU_VERSION).json


# Run qemu to check kernel, for -nographic mode, Ctrl+A X to exit qemu
$(QEMU_TARGETs): ISA = $(subst run_qemu_,,$@)
run_qemu_X86:
	qemu-system-x86_64 -nographic \
		-hda disk_images/ubuntu-$(ISA)-$(UBUNTU_VERSION)-img/ubuntu-$(ISA)-$(UBUNTU_VERSION).img \
		-enable-kvm \
		-m 2048 \
		-kernel linux/arch/x86_64/boot/bzImage \
		-append "root=/dev/hda1 console=ttyS0"
# Uncompress kernel needs qemu version > 4.0
		#-kernel linux/vmlinux-$(ISA)-$(KERNEL_VERSION) \

run_gem5_x86:
	./gem5/build/X86/gem5.opt configs/fs_run.py --script=$(CMD)

stats_gem5_x86:
	./gem5/build/X86/gem5.opt configs/fs_run_stats.py --cpus=1 --script=$(CMD)

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

mcpat:
	make all -C ./mcpat

# Run for the first time
build_docker:
	-mkdir -p $(PWD)/mongodb
	docker container create -p 27017:27017 -v $(PWD)/mongodb:/data/db --name mongo-gem5 mongo

start_docker:
	docker start mongo-gem5

stop_docker:
	docker stop mongo-gem5

