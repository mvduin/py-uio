#!/usr/bin/python3

from uio.ti.icss import Icss
from time import sleep

pruss = Icss( "/dev/uio/pruss/module" )
pruss.initialize()

core = pruss.core0

program = core.load( 'fw/loop-count.dbg' )
iram = core.iram.map().cast('I')
regs = core.r[:]
state = core.state
ins = None
breakpoints = set()
stepping_out_of_bp = None

# whether to single-step
single = False

def clear_breakpoint( pc ):
    if not state.halted:
        raise RuntimeError("PRU core is not halted")
    if pc in breakpoints:
        iram[ pc ] = program.dbginfo[ pc ].opcode
        breakpoints.remove( pc )

def set_breakpoint( pc ):
    if not state.halted:
        raise RuntimeError("PRU core is not halted")
    if pc not in breakpoints:
        assert iram[ pc ] == program.dbginfo[ pc ].opcode
        iram[ pc ] = 0x2a000000  # halt instruction
        breakpoints.add( pc )


set_breakpoint( 2 )
set_breakpoint( 5 )

def done():
    return state.crashed or (ins.opcode & 0xfe000000) == 0x2a000000

def update_state():
    global state, ins, stepping_out_of_bp

    for i in range(3):
        state = core.state
        if not state.halted:
            continue

        ins = program.dbginfo[ core.pc ]

        if stepping_out_of_bp is None:
            return True

        # restore a breakpoint that was temp-disabled to step out of it
        set_breakpoint( stepping_out_of_bp )
        stepping_out_of_bp = None

        if single or done():
            return True

        core.run( single=single )
        return update_state()

    return False

def check():
    # check core state
    if not update_state():
        # can't really do much until it's halted
        print( "%s." % state )
        return True

    # show register changes
    for i, v in enumerate( core.r[:] ):
        if v != regs[i]:
            print( "r%d = %d (0x%x)" % (i, v, v) )
            regs[i] = v

    if not state.crashed:
        # show next instruction
        print( "(%4d)  %s:%d:\t%s" % (ins.index, ins.file, ins.line, ins.text) )

    # detect program end
    if done():
        print( "%s." % state )
        return False

    return True

while check():
    if not state.halted:
        sleep( 0.5 )
        continue

    assert stepping_out_of_bp is None

    if core.pc in breakpoints:
        stepping_out_of_bp = core.pc
        clear_breakpoint( stepping_out_of_bp )
        core.run( single=True )
    else:
        core.run( single=single )

    ins = None
