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
from optparse import OptionParser

spec_dist = os.environ.get('M5_CPU2006', '/dist/m5/cpu2006')

class Benchmark(object):
    def __init__(self, isa, os, size, workload):
        if not hasattr(self.__class__, 'name'):
            self.name = self.__class__.__name__

        if not hasattr(self.__class__, 'binary'):
            self.binary = self.name + '_base.gem5-' + isa
        else:
            self.binary = self.__class__.binary + '_base.gem5-' + isa

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

        full_binary = joinpath(self.run_dir, self.binary)
        if not isfile(full_binary):
            raise AttributeError, '%s not found' % full_binary
        self.executable = self.binary


        if not hasattr(self.__class__, 'stdin'):
            self.stdin = []

        if not hasattr(self.__class__, 'stdout'):
            self.stdout = []

        func(self, isa, workload)

    def makeProcessArgs(self, **kwargs):
        # set up default args for Process object
        process_args = {}
        if self.stdin:
            process_args['input'] = self.stdin
        if self.stdout:
            process_args['output'] = self.stdout
        if self.simpoint:
            process_args['simpoint'] = self.simpoint
        # explicit keywords override defaults
        process_args.update(kwargs)

        cwd = process_args.get('cwd')
        if not cwd:
            pass
        else:
            process_args['cmd'] = [ joinpath(cwd, self.executable) ] + self.args
            process_args['executable'] = joinpath(cwd, self.executable)


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

    def __init__(self, isa, os, size, workload):
        Benchmark.__init__(self, isa, os, size, workload)

    def com(self, isa, sz, wrkld):
        if wrkld in self.opts[sz].keys():
            self.args = self.opts[sz][wrkld]
        elif 'all' == wrkld:
            for wl in self.opts[sz].keys():
                self.args = self.args + [self.opts[sz][wl]]
        else:
            print("No workload args for %s" % wrkld)
            pass

        if wrkld in self.inputs[sz].keys():
            self.stdin = self.inputs[sz][wrkld]
        elif 'all' == wrkld:
            for wl in self.inputs[sz].keys():
                self.stdin = self.stdin + [self.inputs[sz][wl]]
        else:
            print("No workload stdin for %s" % wrkld)
            pass

    def ref(self, isa, wrkld):
        self.com(isa, 'ref', wrkld)

    def test(self, isa, wrkld):
        self.com(isa, 'test', wrkld)


# opts can be found by command `specinvoke -n` in run dir
class perlbench(DefaultBenchmark):
    name = 'perlbench'
    number = 400

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['checkspam'] = [
                    '-I./lib', 'checkspam.pl',
                    '2500', '5', '25', '11', '150', '1', '1', '1', '1'
                    ]
        self.opts['ref']['diffmail'] = [
                    '-I./lib', 'diffmail.pl',
                    '4', '800', '10', '17', '19', '300'
                    ]
        self.opts['ref']['splitmail'] = [
                    '-I./lib splitmail.pl',
                    '1600', '12', '26', '16', '4500'
                    ]
        DefaultBenchmark.__init__(self, isa, os, size, workload)


class bzip2(DefaultBenchmark):
    name = 'bzip2'
    number = 401

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['source'] = ['input.source', '280']
        self.opts['ref']['chicken'] = ['chicken.jpg', '30']
        self.opts['ref']['liberty'] = ['liberty.jpg', '30']
        self.opts['ref']['program'] = ['input.program', '280']
        self.opts['ref']['text'] = ['text.html', '280']
        self.opts['ref']['combined'] = ['input.combined', '200']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class gcc(DefaultBenchmark):
    name = 'gcc'
    number = 403

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['166'] = ['166.in']
        self.opts['ref']['200'] = ['200.in']
        self.opts['ref']['c-typeck'] = ['c-typeck.in']
        self.opts['ref']['cp-decl'] = ['cp-decl.in']
        self.opts['ref']['expr'] = ['expr.in']
        self.opts['ref']['expr2'] = ['expr2.in']
        self.opts['ref']['g23'] = ['g23.in']
        self.opts['ref']['s04'] = ['s04.in']
        self.opts['ref']['scilab'] = ['scilab.in']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class bwaves(DefaultBenchmark):
    name = 'bwaves'
    number = 410
    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        DefaultBenchmark.__init__(self, isa, os, size, workload)

class gamess(DefaultBenchmark):
    name = 'gamess'
    number = 416

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.inputs['ref']['cytosine'] = ['cytosine.2.config']
        self.inputs['ref']['h2ocu2+'] = ['h2ocu2+.gradient.config']
        self.inputs['ref']['triazolium'] = ['triazolium.config']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class mcf(DefaultBenchmark):
    name = 'mcf'
    number = 429

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['inp'] = ['inp.in']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class milc(DefaultBenchmark):
    name = 'milc'
    number = 433

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.inputs['ref']['su3imp'] = ['su3imp.in']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class zeusmp(DefaultBenchmark):
    name = 'zeusmp'
    number = 434

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        DefaultBenchmark.__init__(self, isa, os, size, workload)

class gromacs(DefaultBenchmark):
    name = 'gromacs'
    number = 435

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['gromacs'] = ['-silent', '-deffnm', 'gromacs', '-nice', '0']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class cactusADM(DefaultBenchmark):
    name = 'cactusADM'
    number = 436

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['benchADM'] = ['benchADM.par']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class leslie3d(DefaultBenchmark):
    name = 'leslie3d'
    number = 437

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.inputs['ref']['leslie3d'] = ['leslie3d.in']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class namd(DefaultBenchmark):
    name = 'namd'
    number = 444

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['namd'] = ['--input', 'namd.input', '--iterations', '38', '--output', 'namd.out']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class gobmk(DefaultBenchmark):
    name = 'gobmk'
    number = 445

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['13x13'] = ['--quiet', '--mode', 'gtp']
        self.opts['ref']['nngs'] = ['--quiet', '--mode', 'gtp']
        self.opts['ref']['score2'] = ['--quiet', '--mode', 'gtp']
        self.opts['ref']['trevorc'] = ['--quiet', '--mode', 'gtp']
        self.opts['ref']['trevord'] = ['--quiet', '--mode', 'gtp']

        self.inputs['ref']['13x13'] = ['13x13.tst']
        self.inputs['ref']['nngs'] = ['nngs.tst']
        self.inputs['ref']['score2'] = ['score2.tst']
        self.inputs['ref']['trevorc'] = ['trevorc']
        self.inputs['ref']['trevord'] = ['trevord']

        DefaultBenchmark.__init__(self, isa, os, size, workload)

class dealII(DefaultBenchmark):
    name = 'dealII'
    number = 447

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['ref'] = ['23']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class soplex(DefaultBenchmark):
    name = 'soplex'
    number = 450

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['pds-50'] = ['-m4500', 'pds-50.mps']
        self.opts['ref']['ref'] = ['-m3500', 'ref.mps']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class povray(DefaultBenchmark):
    name = 'povray'
    number = 453

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['SPEC-benchmark'] = ['SPEC-benchmark-ref.ini']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class calculix(DefaultBenchmark):
    name = 'calculix'
    number = 454

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['hyperviscoplastic'] = ['-i', 'hyperviscoplastic']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class hmmer(DefaultBenchmark):
    name = 'hmmer'
    number = 456

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['nph3'] = ['nph3.hmm', 'swiss41']
        self.opts['ref']['retro'] = ['--fixed', '0', '--mean', '500' '--num', '500000', '--sd', '350', '--seed', '0', 'retro.hmm']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class sjeng(DefaultBenchmark):
    name = 'sjeng'
    number = 458

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['ref'] = ['ref.txt']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class GemsFDTD(DefaultBenchmark):
    name = 'GemsFDTD'
    number = 459

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        DefaultBenchmark.__init__(self, isa, os, size, workload)

class libquantum(DefaultBenchmark):
    name = 'libquantum'
    number = 462

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['ref'] = ['1397', '8']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class h264ref(DefaultBenchmark):
    name = 'h264ref'
    number = 464

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['forman_baseline'] = ['-d','foreman_ref_encoder_baseline.cfg']
        self.opts['ref']['forman_main'] = ['-d','foreman_ref_encoder_baseline.cfg']
        self.opts['ref']['sss_main'] = ['-d','sss_encoder_main.cfg']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class tonto(DefaultBenchmark):
    name = 'tonto'
    number = 465

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        DefaultBenchmark.__init__(self, isa, os, size, workload)

class lbm(DefaultBenchmark):
    name = 'lbm'
    number = 470

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['reference'] = ['3000', 'reference.dat', '0', '0', '100_100_130_ldc.of']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class omnetpp(DefaultBenchmark):
    name = 'omnetpp'
    number = 471

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['omnetpp'] = ['omnetpp.ini']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class astar(DefaultBenchmark):
    name = 'astar'
    number = 473

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['rivers'] = ['rivers.cfg']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class wrf(DefaultBenchmark):
    name = 'wrf'
    number = 481

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        DefaultBenchmark.__init__(self, isa, os, size, workload)

class sphinx3(DefaultBenchmark):
    name = 'sphinx3'
    binary = 'sphinx_livepretend'
    number = 482

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['an4'] = ['ctlfile' '.' 'args.an4']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class xalancbmk(DefaultBenchmark):
    name = 'xalancbmk'
    binary = 'Xalan'
    number = 483

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['t5'] = ['t5.xml' 'xalanc.xsl']
        DefaultBenchmark.__init__(self, isa, os, size, workload)


class specrand_int(DefaultBenchmark):
    name = 'specrand'
    number = 998

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['ref'] = ['1255432124', '234923']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

class specrand_fp(DefaultBenchmark):
    name = 'specrand'
    number = 999

    def __init__(self, isa, os, size, workload):
        self.opts = {}
        self.opts['ref'] = {}
        self.opts['test'] = {}
        self.inputs = {}
        self.inputs['ref'] = {}
        self.inputs['test'] = {}

        self.opts['ref']['ref'] = ['1255432124', '234923']
        DefaultBenchmark.__init__(self, isa, os, size, workload)

cpu2006int = [
        perlbench, bzip2, gcc, mcf,
        gobmk, hmmer, sjeng, libquantum,
        h264ref, omnetpp, astar, xalancbmk,
        specrand_int
    ]

cpu2006fp = [
        bwaves, gamess, milc, zeusmp,
        gromacs, cactusADM, leslie3d, namd,
        dealII, soplex, povray, calculix,
        GemsFDTD, tonto, lbm, wrf,
        sphinx3, specrand_fp
    ]

all = cpu2006int + cpu2006fp

__all__ = [ x.__name__ for x in all ]

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-l", "--list", action="store_true", dest="list", default=False)
    parser.add_option("-g", "--generate", action="store_true", dest="generate", default=False)
    (opts, args) = parser.parse_args()

    if opts.list:
        from pprint import pprint
        for bench in all:
            for size in ['ref']:
                print('class: %s' % bench.__name__)
                x = bench('x86', 'linux', size, 'all')
                print('%s %s workloads: %s' % (bench.__name__, size, list(set(x.opts[size].keys()))))
                pprint(x.makeProcessArgs())
                print()
    elif opts.generate:
        for bench in all:
            for size in ['ref']:
                print('class: %s' % bench.__name__)
                x = bench('x86', 'linux', size, 'all')
                print('%s %s workloads: %s' % (bench.__name__, size, list(set(x.opts[size].keys()))))
                wrklds = list(set(x.opts[size].keys()))
                for wrkld in wrklds:
                    x = bench('x86', 'linux', size, wrkld)
                    with open('./m5tools/' + str(x.number) + '.' + ('.'.join([x.name, size, wrkld])) + '.sh', 'w') as f:
                        print('#!/bin/bash', file=f)
                        print('cd ${M5_CPU2006}/benchspec/CPU2006/' + str(x.number) + '.' + x.name + '/run/run_base_' + size + '_gem5-x86.0000', file=f)
                        print('./' + x.executable + ' ' + (' '.join(x.args)) + ' \\', file=f)
                        print('    ' + '1>' + ('.'.join([x.name, size, wrkld, 'out'])) + ' \\', file=f)
                        print('    ' + '2>' + ('.'.join([x.name, size, wrkld, 'err'])), file=f)
                        print('if [-s /sbin/m5]', file=f)
                        print('then', file=f)
                        print('    /sbin/m5 writefile ' + ('.'.join([x.name, size, wrkld, 'out'])) + ' ' + ('.'.join([x.name, size, wrkld, 'simout'])), file=f)
                        print('    /sbin/m5 writefile ' + ('.'.join([x.name, size, wrkld, 'err'])) + ' ' + ('.'.join([x.name, size, wrkld, 'simerr'])), file=f)
                        print('fi', file=f)
                    f.close()
