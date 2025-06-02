# This makefile include most useful target of gem5

DEBUG ?= 0

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
MOUNT_TARGETs = $(foreach ISA, $(ISAs), mount_img_$(ISA))
UMOUNT_TARGETs = $(foreach ISA, $(ISAs), umount_img_$(ISA))


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
BENCHMARK ?=
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

empty :=
space :=$(empty) $(empty)
# Build Full System disk
ifeq ($(DEBUG), 1)
# Let packer output debug log
export PACKER_LOG=1
endif
UBUNTU_VERSION ?= 18.04
$(IMAGE_TARGETs): ISA = $(subst build_img_,,$@)
$(IMAGE_TARGETs): IMG_SUFFIX = $(subst $(space),-,$(strip $(ISA) $(UBUNTU_VERSION) $(BENCHMARK)))
$(IMAGE_TARGETs): $(build_util_$(ISA))
	@echo "Building disk image with Ubuntu $(UBUNTU_VERSION) $(ISA) $(BENCHMARK)"
	packer validate packer_configs/ubuntu-$(IMG_SUFFIX).json
	packer build packer_configs/ubuntu-$(IMG_SUFFIX).json |& tee packer.log


# Run qemu to check kernel, for -nographic mode, Ctrl+A X to exit qemu
$(QEMU_TARGETs): ISA = $(subst run_qemu_,,$@)
$(QEMU_TARGETs): IMG_SUFFIX = $(subst $(space),-,$(strip $(ISA) $(UBUNTU_VERSION) $(BENCHMARK)))
run_qemu_X86:
	qemu-system-x86_64 -nographic \
		-hda disk_images/ubuntu-$(IMG_SUFFIX)-img/ubuntu-$(IMG_SUFFIX).img \
		-enable-kvm \
		-m 4096 \
		-kernel linux/arch/x86_64/boot/bzImage \
		-append "root=/dev/hda1 console=ttyS0"
# Uncompress kernel needs qemu version > 4.0, which is support ubuntu 20.04 and later
		#-kernel linux/vmlinux-$(ISA)-$(KERNEL_VERSION)

# TODO: Not test yet
run_qemu_ARM:
	qemu-system-aarch64 -nographic \
		-hda disk_images/ubuntu-$(IMG_SUFFIX)-img/ubuntu-$(IMG_SUFFIX).img \
		-enable-kvm \
		-m 4096 \
		-kernel linux/arch/arm64/boot/bzImage \
		-append "root=/dev/hda1 console=ttyS0"
# Uncompress kernel needs qemu version > 4.0, which is support ubuntu 20.04 and later
		#-kernel linux/vmlinux-$(ISA)-$(KERNEL_VERSION)

# TODO: Not test yet
run_qemu_RISCV:
	qemu-system-riscv -nographic \
		-hda disk_images/ubuntu-$(ISA)-$(UBUNTU_VERSION)-img/ubuntu-$(ISA)-$(UBUNTU_VERSION).img \
		-enable-kvm \
		-m 4096 \
		-kernel linux/arch/riscv/boot/bzImage \
		-append "root=/dev/hda1 console=ttyS0"
# Uncompress kernel needs qemu version > 4.0, which is support ubuntu 20.04 and later
		#-kernel linux/vmlinux-$(ISA)-$(KERNEL_VERSION) \

# Build util for full system
build_util_X86:
	cd gem5/util/m5; \
		scons build/x86/out/m5

build_util_ARM:
	cd gem5/util/m5; \
		scons CROSS_COMPILE=aarch64-linux-gnu- build/arm64/out/m5

build_util_RISCV:
	cd gem5/util/m5; \
		scons CROSS_COMPILE=riscv64-linux-gnu- build/riscv/out/m5

run_gem5_X86:
	./gem5/build/X86/gem5.opt configs/fs_run.py --script=$(CMD)

stats_gem5_x86:
	./gem5/build/X86/gem5.opt configs/fs_run_stats.py --cpus=1 --script=$(CMD)


# Debug commands
$(MOUNT_TARGETs): ISA = $(subst mount_img_,,$@)
$(MOUNT_TARGETs): IMG_SUFFIX = $(subst $(space),-,$(strip $(ISA) $(UBUNTU_VERSION) $(BENCHMARK)))
$(MOUNT_TARGETs):
	sudo kpartx -av \
		disk_images/ubuntu-$(IMG_SUFFIX)-img/ubuntu-$(IMG_SUFFIX).img
	@sleep 1
	sudo mount /dev/mapper/loop0p1 /mnt

$(UMOUNT_TARGETs): ISA = $(subst umount_img_,,$@)
$(UMOUNT_TARGETs): IMG_SUFFIX = $(subst $(space),-,$(strip $(ISA) $(UBUNTU_VERSION) $(BENCHMARK)))
$(UMOUNT_TARGETs):
	sudo umount /mnt
	sudo kpartx -dv \
		disk_images/ubuntu-$(IMG_SUFFIX)-img/ubuntu-$(IMG_SUFFIX).img

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

