# Copyright (c) 2006-2008 The Regents of The University of Michigan
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
# Authors: Nathan Binkert

from __future__ import print_function

import os
import sys
from os.path import basename, exists, join as joinpath, normpath
from os.path import isdir, isfile, islink

spec_dist = os.environ.get('M5_CPU2006', '/dist/m5/cpu2006')

class Benchmark(object):
    def __init__(self, isa, os, size, workload):
        if not hasattr(self.__class__, 'name'):
            self.name = self.__class__.__name__

        if not hasattr(self.__class__, 'binary'):
            self.binary = self.name + '_base.gem5-' + isa

        if not hasattr(self.__class__, 'args'):
            self.args = []

        if not hasattr(self.__class__, 'output'):
            self.output = '%s.out' % self.name

        if not hasattr(self.__class__, 'simpoint'):
            self.simpoint = None


        self.size = size
        try:
            func = getattr(self.__class__, size)
        except AttributeError:
            raise AttributeError, \
                  'The benchmark %s does not have the %s workload' % \
                  (self.name, size)

        self.run_dir = joinpath(
                spec_dist, 'benchspec', 'CPU2006', str(self.number) + '.' + self.name,
                'run', 'run_base_' + size + '_gem5-' + isa + '.0000')

        executable = joinpath(self.run_dir, self.binary)
        if not isfile(executable):
            raise AttributeError, '%s not found' % executable
        self.executable = executable


        if not hasattr(self.__class__, 'stdin'):
            self.stdin = joinpath(self.run_dir, '%s.in' % self.name)
            if not isfile(self.stdin):
                self.stdin = None

        if not hasattr(self.__class__, 'stdout'):
            self.stdout = joinpath(self.run_dir, '%s.out' % self.name)
            if not isfile(self.stdout):
                self.stdout = None

        func(self, isa, workload)

    def makeProcessArgs(self, **kwargs):
        # set up default args for Process object
        process_args = {}
        process_args['cmd'] = [ self.executable ] + self.args
        process_args['executable'] = self.executable
        if self.stdin:
            process_args['input'] = self.stdin
        if self.stdout:
            process_args['output'] = self.stdout
        if self.simpoint:
            process_args['simpoint'] = self.simpoint
        # explicit keywords override defaults
        process_args.update(kwargs)

        return process_args

    def makeProcess(self, **kwargs):
        process_args = self.makeProcessArgs(**kwargs)

        # figure out working directory: use m5's outdir unless
        # overridden by Process's cwd param
        cwd = process_args.get('cwd')
        if not cwd:
            from m5 import options
            cwd = options.outdir
            process_args['cwd'] = cwd
        if not isdir(cwd):
            os.makedirs(cwd)

        # copy all run files to current working directory
        os.system("cp -rf %s/* %s/." % (self.run_dir, cwd))

        # generate Process object
        from m5.objects import Process
        return Process(**process_args)

    def __str__(self):
        return self.name

class DefaultBenchmark(Benchmark):
    def ref(self, isa, workload): pass
    def test(self, isa, workload): pass
    def train(self, isa, workload): pass

class perlbench(DefaultBenchmark):
    name = 'perlbench'
    number = 400
    opts = {}
    opts['ref'] = {}
    opts['ref']['checkspam'] = [
            '-I./lib', 'checkspam.pl',
            '2500', '5', '25', '11', '150', '1', '1', '1', '1'
            ]
    opts['ref']['diffmail'] = [
            '-I./lib', 'diffmail.pl',
            '4', '800', '10', '17', '19', '300'
            ]
    opts['ref']['splitmail'] = [
            '-I./lib splitmail.pl',
            '1600', '12', '26', '16', '4500'
            ]

    opts['test'] = {}

    def com(self, isa, sz, wrkld):
        if wrkld in self.opts[sz].keys():
            self.args = self.opts[sz][wrkld]
        elif 'all' == wrkld:
            for wl in self.opts[sz].keys():
                self.args = self.args + [self.opts[sz][wl]]
        else:
            raise AttributeError, "No workload %s found" % wrkld

    def ref(self, isa, wrkld):
        self.com(isa, 'ref', wrkld)

    def test(self, isa, wrkld):
        self.com(isa, 'test', wrkld)



cpu2006int = [ perlbench ]
#cpu2006int = [
#        perlbench, bzip2, gcc, mcf,
#        gobmk, hmmer, sjeng, libquantum,
#        h264ref, omnetpp, astar, xalancbmk,
#        specrand_int
#    ]
#
cpu2006fp = []
#cpu2006fp = [
#        bwaves, gamess, milc, zeusmp,
#        gromacs, cactusADM, leslie3d, namd,
#        dealII, soplex, povray, calculix,
#        GemsFDTD, tonto, lbm, wrf,
#        sphinx3, specrand_fp
#    ]

all = cpu2006int + cpu2006fp

__all__ = [ x.__name__ for x in all ]

if __name__ == '__main__':
    from pprint import pprint
    for bench in all:
        for size in ['ref']:
            print('class: %s' % bench.__name__)
            x = bench('x86', 'linux', size, 'all')
            print('%s: %s' % (x, size))
            pprint(x.makeProcessArgs())
            print()
