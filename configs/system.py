# -*- coding: utf-8 -*-
# Copyright (c) 2016 Jason Lowe-Power
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Jason Lowe-Power

import m5
from m5.objects import *
from m5.util import convert

import x86_mp
from caches import *

import SimpleOpts

class SimSystem(LinuxX86System):

    SimpleOpts.add_option("--no_host_parallel", default=False,
                action="store_true",
                help="Do NOT run gem5 on multiple host threads (kvm only)")

    SimpleOpts.add_option("--cpus", default=2, type="int",
                          help="Number of CPUs in the system")

    def __init__(self, opts, no_kvm=False):
        super(SimSystem, self).__init__()
        self._opts = opts
        self._no_kvm = no_kvm

        self._host_parallel = (not self._opts.no_host_parallel) & (not no_kvm)

        # Set up the clock domain and the voltage domain
        self.clk_domain = SrcClockDomain()
        self.clk_domain.clock = '3GHz'
        self.clk_domain.voltage_domain = VoltageDomain()

        # For x86, there is an I/O gap from 3GB to 4GB.
        # We can have at most 3GB of memory unless we do something special
        # to account for this I/O gap. For simplicity, this is omitted.
        mem_size = '2048MB'
        self.mem_ranges = [
                            AddrRange(mem_size),
                            AddrRange(0xC0000000, size=0x100000), # For I/0
                          ]

        # Create the main memory bus
        # This connects to main memory
        self.membus = SystemXBar(width = 64)
        self.membus.badaddr_responder = BadAddr()
        self.membus.default = self.membus.badaddr_responder.pio

        # Set up the system port for functional access from the simulator
        self.system_port = self.membus.slave

        # This will initialize most of the x86-specific system parameters
        # This includes things like the I/O, multiprocessor support, BIOS...
        x86_mp.init_fs(self, self.membus, self._opts.cpus)
        #x86.init_fs(self, self.membus)

        # Change this path to point to the kernel you want to use
        # Kernel from http://www.m5sim.org/dist/current/x86/x86-system.tar.bz2
        self.kernel = 'linux/vmlinux'

        # Options specified on the kernel command line
        boot_options = ['earlyprintk=ttyS0', 'console=ttyS0', 'lpj=7999923',
                        'root=/dev/hda1']
        self.boot_osflags = ' '.join(boot_options)

        # Replace these paths with the path to your disk images.
        # The first disk is the root disk. The second could be used for swap
        # or anything else.
        # Disks from http://www.m5sim.org/dist/current/x86/x86-system.tar.bz2
        self.setDiskImage('ubuntu-1604.X86.img')

        # Create the CPU for our system.
        self.createCPU()

        # Create the cache heirarchy for the system.
        self.createCacheHierarchy()

        # Create the memory controller for the sytem
        self.createMemoryControllers()

        # Set up the interrupt controllers for the system (x86 specific)
        self.setupInterrupts()

        if self._host_parallel:
            # To get the KVM CPUs to run on different host CPUs
            # Specify a different event queue for each CPU
            for i,cpu in enumerate(self.cpu):
                for obj in cpu.descendants():
                    obj.eventq_index = 0
                cpu.eventq_index = i + 1

    def getHostParallel(self):
        return self._host_parallel

    def createCPU(self):
        """ Create a CPU for the system """
        # This defaults to one simple atomic CPU. Using other CPU models
        # and using timing memory is possible as well.
        # Also, changing this to using multiple CPUs is also possible
        # Note: If you use multiple CPUs, then the BIOS config needs to be
        #       updated as well.

        if self._no_kvm:
            self.cpu = [AtomicSimpleCPU(cpu_id = i, switched_out = False)
                              for i in range(self._opts.cpus)]
            self.mem_mode = 'atomic'
        else:
            # Note KVM needs a VM and atomic_noncaching
            self.cpu = [X86KvmCPU(cpu_id = i)
                            for i in range(self._opts.cpus)]
            self.kvm_vm = KvmVM()
            self.mem_mode = 'atomic_noncaching'

            self.atomicCpu = [AtomicSimpleCPU(cpu_id = i, switched_out = True)
                                for i in range(self._opts.cpus)]
            for cpu in self.atomicCpu:
                cpu.createThreads()

        self.timingCpu = [DerivO3CPU(cpu_id = i, switched_out = True)
                            for i in range(self._opts.cpus)]
        for cpu in self.timingCpu:
            cpu.createThreads()

        for cpu in self.cpu:
            cpu.createThreads()

    def switchCpus(self, old, new):
        assert(new[0].switchedOut())
        m5.switchCpus(self, zip(old, new))

    def setDiskImage(self, img_path):
        """ Set the disk image
            @param img_path path on the host to the image file for the disk
        """
        # Can have up to two master disk images.
        # This can be enabled with up to 4 images if using master-slave pairs
        disk0 = CowDisk(img_path)
        self.pc.south_bridge.ide.disks = [disk0]

    def createCacheHierarchy(self):
        """ Create a simple cache heirarchy with the caches"""

        # Create an L3 cache (with crossbar)
        self.l3bus = L2XBar(width = 64,
                            snoop_filter = SnoopFilter(max_capacity='32MB'))

        for cpu in self.cpu:
            # Create a memory bus, a coherent crossbar, in this case
            cpu.l2bus = L2XBar()

            # Create an L1 instruction and data cache
            cpu.icache = L1ICache(self._opts)
            cpu.dcache = L1DCache(self._opts)
            cpu.mmucache = MMUCache()

            # Connect the instruction and data caches to the CPU
            cpu.icache.connectCPU(cpu)
            cpu.dcache.connectCPU(cpu)
            cpu.mmucache.connectCPU(cpu)

            # Hook the CPU ports up to the l2bus
            cpu.icache.connectBus(cpu.l2bus)
            cpu.dcache.connectBus(cpu.l2bus)
            cpu.mmucache.connectBus(cpu.l2bus)

            # Create an L2 cache and connect it to the l2bus
            cpu.l2cache = L2Cache(self._opts)
            cpu.l2cache.connectCPUSideBus(cpu.l2bus)

            # Connect the L2 cache to the L3 bus
            cpu.l2cache.connectMemSideBus(self.l3bus)

        self.l3cache = L3Cache(self._opts)
        #self.l3cache = L3Cache(self._opts)
        self.l3cache.connectCPUSideBus(self.l3bus)

        # Connect the L3 cache to the membus
        self.l3cache.connectMemSideBus(self.membus)

    def createMemoryControllers(self):
        """ Create the memory controller for the system """

        # Just create a controller for the first range, assuming the memory
        # size is < 3GB this will work. If it's > 3GB or if you want to use
        # mulitple or interleaved memory controllers then this should be
        # updated accordingly
        self.mem_cntrl = DDR3_1600_8x8(range = self.mem_ranges[0],
                                       port = self.membus.master)

    def setupInterrupts(self):
        """ Create the interrupt controller for the CPU """

        for cpu in self.cpu:
            # create the interrupt controller CPU and connect to the membus
            cpu.createInterruptController()

            # For x86 only, connect interrupts to the memory
            # Note: these are directly connected to the memory bus and
            #       not cached
            cpu.interrupts[0].pio = self.membus.master
            cpu.interrupts[0].int_master = self.membus.slave
            cpu.interrupts[0].int_slave = self.membus.master

class CowDisk(IdeDisk):
    """ Wrapper class around IdeDisk to make a simple copy-on-write disk
        for gem5. Creates an IDE disk with a COW read/write disk image.
        Any data written to the disk in gem5 is saved as a COW layer and
        thrown away on the simulator exit.
    """

    def __init__(self, filename):
        """ Initialize the disk with a path to the image file.
            @param filename path to the image file to use for the disk.
        """
        super(CowDisk, self).__init__()
        self.driveID = 'master'
        self.image = CowDiskImage(child=RawDiskImage(read_only=True),
                                  read_only=False)
        self.image.child.image_file = filename
