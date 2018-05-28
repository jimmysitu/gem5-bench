# This makefile include most useful target of Gem5

ISO_URL  = 'http://releases.ubuntu.com/xenial'
ISO_NAME = 'ubuntu-16.04.4-server-amd64.iso'

ISAs := X86 ARM RISCV
exts := opt prof perf debug

BUILD_SPECs = $(foreach ISA, $(ISAs), BUILD_SPEC2006_$(ISA))
SETUP_SPECs = $(foreach ISA, $(ISAs), SETUP_SPEC2006_$(ISA))
RUN_SPECs = $(foreach ISA, $(ISAs), RUN_SPEC2006_$(ISA))
CLEAN_SPECs = $(foreach ISA, $(ISAs), CLEAN_SPEC2006_$(ISA))

GEM5_TARGETs = $(foreach ISA, $(ISAs), $(foreach ext, $(exts),  gem5/build/$(ISA)/gem5.$(ext)))


.PHONY: check-env check-isa check-wrkld $(BUILD_SPECs) $(SETUP_SPECs) $(RUN_SPECs) $(CLEAN_SPECs)

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
	$(error WRKLD is undefined)
endif


# Build SPEC2006 for gem5
$(BUILD_SPECs): check-env
	cp ${PWD}/spec2006_configs/gem5-$(subst BUILD_SPEC2006_,,$@).cfg ${PWD}/spec2006_configs/gem5-$(subst BUILD_SPEC2006_,,$@).bld.cfg; \
	cd ${M5_CPU2006}; \
	. ./shrc; \
	runspec --action=build --tuning=base --noreportable --config ${PWD}/spec2006_configs/gem5-$(subst BUILD_SPEC2006_,,$@).bld.cfg int; \
	runspec --action=build --tuning=base --noreportable --config ${PWD}/spec2006_configs/gem5-$(subst BUILD_SPEC2006_,,$@).bld.cfg fp; \
	echo "$(@) build done"

# Setup the run dir before gem5 simulation
$(SETUP_SPECs): check-env
	cp ${PWD}/spec2006_configs/gem5-$(subst SETUP_SPEC2006_,,$@).cfg ${PWD}/spec2006_configs/gem5-$(subst SETUP_SPEC2006_,,$@).bld.cfg; \
	cd ${M5_CPU2006}; \
	. ./shrc; \
	runspec --action=setup --tuning=base -i ref -n 1 --noreportable --config ${PWD}/spec2006_configs/gem5-$(subst SETUP_SPEC2006_,,$@).bld.cfg int; \
	runspec --action=setup --tuning=base -i ref -n 1 --noreportable --config ${PWD}/spec2006_configs/gem5-$(subst SETUP_SPEC2006_,,$@).bld.cfg fp; \
	echo "$(@) run done"

# Try run on native machine before gem5 simulation
$(RUN_SPECs): check-env
	cd ${M5_CPU2006}; \
	. ./shrc; \
	runspec --action=run --tuning=base -i ref -n 1 --noreportable --config ${PWD}/spec2006_configs/gem5-$(subst RUN_SPEC2006_,,$@).bld.cfg int; \
	runspec --action=run --tuning=base -i ref -n 1 --noreportable --config ${PWD}/spec2006_configs/gem5-$(subst RUN_SPEC2006_,,$@).bld.cfg fp; \
	echo "$(@) run done"

# Clean SPEC2006 for gem5
$(CLEAN_SPECs): check-env
	cd ${M5_CPU2006}; \
	. ./shrc; \
	runspec --action=clean --config ${PWD}/spec2006_configs/gem5-$(subst CLEAN_SPEC2006_,,$@).bld.cfg int; \
	runspec --action=clean --config ${PWD}/spec2006_configs/gem5-$(subst CLEAN_SPEC2006_,,$@).bld.cfg fp; \
	rm ${PWD}/spec2006_configs/gem5-$(subst CLEAN_SPEC2006_,,$@).bld.cfg; \
	echo "$(@) clean done"

# Build gem5
$(GEM5_TARGETs): gem5/src
	cd gem5; \
	scons -j 4 $(subst gem5/,,$@)

build_gem5_all: $(GEM5_TARGETs)
	echo "Build All Targets Done"


# Build Full System ISO
build_img:
	echo "TODO"

# TODO: Long run for this simulation, slurm should be used
# SE Mode
perlbench: check-isa check-wrkld 
	./gem5/build/$(ISA)/gem5.opt configs/se_cpu2006.py --bench=perlbench --spec-workload=$(WRKLD)



