#!/usr/bin/python3

from mako.template import Template
import os

mkt = Template(filename='./m5tools/gem5init.mkt')
with open('./m5tools/gem5init', 'w') as out:
    print(mkt.render(M5_CPU2006=os.environ['M5_CPU2006']), file=out)

