#!/usr/bin/python3

from uio.ti.icss import Icss
from time import sleep

pruss = Icss( "/dev/uio/pruss/module" )
pruss.initialize()

core = pruss.core0

program = core.load( 'fw/test.dbg' )
regs = core.r[:]
state = None
ins = None

def check():
    global state, ins

    # check core state
    for i in range(3):
        state = core.state
        if state.halted:
            break

    # can't really do much until it's halted
    if not state.halted:
        print( "%s." % state )
        return True

    # show register changes
    for i, v in enumerate( core.r[:] ):
        if v != regs[i]:
            print( "r%d = %d (0x%x)" % (i, v, v) )
            regs[i] = v

    if not state.crashed:
        # show next instruction
        ins = program.dbginfo[ core.pc ]
        print( "(%4d)  %s:%d:\t%s" % (ins.index, ins.file, ins.line, ins.text) )

    # detect program end
    if state.crashed or (ins.opcode & 0xfe000000) == 0x2a000000:
        print( "%s." % state )
        return False

    return True

# whether to single-step
single = True

while check():
    if state.halted:
        core.run( single=single )
    else:
        sleep( 0.5 )
