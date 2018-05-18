# This makefile include most useful target of Gem5

ISO_URL  = 'http://releases.ubuntu.com/xenial'
ISO_NAME = 'ubuntu-16.04.4-server-amd64.iso'

ISAs := X86 ARM RISCV
exts := opt prof perf debug  

TARGETs = $(foreach ISA, $(ISAs), $(foreach ext, $(exts),  gem5/build/$(ISA)/gem5.$(ext)))

# Build gem5
$(TARGETs): gem5/src
	cd gem5; \
	scons -j 4 $(subst gem5/,,$@)



build_gem5_all: $(TARGETs)
	echo "Build All Targets Done"


build_img:
	echo "TODO"
