import os
import re
from os import O_RDWR, O_CLOEXEC, O_NONBLOCK
from stat import S_ISCHR
from mmap import mmap
from pathlib import Path

PAGE_SHIFT = 12
PAGE_SIZE = 1 << PAGE_SHIFT
PAGE_MASK = -PAGE_SIZE

class MemRegion:
    def __init__( rgn, uio, info ):
        rgn.uio = uio
        rgn.index = int( re.fullmatch( r'map([0-9])', info.name ).group(1) )

        def getinfo( attr ):
            with (info/attr).open() as f:
                return f.readline().rstrip()

        # If no name has been supplied, the region gets an auto-generated name
        # containing the full DT path.  These are useless, ignore them.
        rgn.name = getinfo( 'name' )
        if rgn.name == '' or rgn.name[0] == '/':
            rgn.name = None

        # get memory region bounds
        rgn.address = int( getinfo('addr'), 0 )
        rgn.size = int( getinfo('size'), 0 )
        rgn.end = rgn.address + rgn.size

        # size that can be actually mmap()ed
        if rgn.address & ~PAGE_MASK:
            rgn.mappable = 0   # not page-aligned, can't be mapped
        else:
            rgn.mappable = rgn.size & PAGE_MASK

        # mmap() is done lazily when needed
        rgn._mmap = None

    def __contains__( rgn, child ):
        return child.address >= rgn.address and child.end <= rgn.end

    def offset( rgn, child ):
        if child not in rgn:
            raise RuntimeError( "not a child region" )
        return child.address - rgn.address

    def map( rgn, struct, offset=0 ):
        if not rgn._mmap:
            if not rgn.mappable:
                raise RuntimeError( "region is not mappable" )

            # UIO uses a disgusting hack where the memory map index is
            # passed via the offset argument.  In the actual kernel call
            # the offset (and length) are in pages rather than bytes, hence
            # we actually need to pass index * PAGE_SIZE as offset.
            rgn._mmap = mmap( rgn.uio._fd, rgn.mappable,
                            offset = rgn.index * PAGE_SIZE )

        if isinstance( offset, Uio ):
            offset = offset.region()
        if isinstance( offset, MemRegion ):
            offset = rgn.offset( offset )
        return struct.from_buffer( rgn._mmap, offset )


# uio device object
class Uio:
    def fileno( self ):
        return self._fd

    def __init__( self, path, blocking=True, parent=None ):
        path = Path( '/dev/uio', path )
        self.path = path

        flags = O_RDWR | O_CLOEXEC
        if not blocking:
            flags |= O_NONBLOCK # for irq_recv
        self._fd = os.open( str(path), flags )

        # parent memory region (if any)
        if parent is not None:
            if isinstance( parent, Uio ):
                parent = parent.region()
            elif isinstance( parent, MemRegion ):
                raise TypeError
        self.parent = parent

        # build path to sysfs dir for obtaining metadata
        dev = os.stat( self._fd ).st_rdev
        dev = '{0}:{1}'.format( os.major(dev), os.minor(dev) )
        self.syspath = Path('/sys/dev/char', dev).resolve()

        # enumerate memory regions
        # beware that if there are none, the dir is absent rather than empty
        self._regions = {}
        rgninfo = self.syspath/'maps';
        if rgninfo.is_dir():
            for info in rgninfo.iterdir():
                rgn = MemRegion( self, info )

                # sanity check
                if parent is not None and rgn not in parent:
                    raise RuntimeError( "memory region outside parent" )

                # allow lookup by index or (if available) by name
                self._regions[ rgn.index ] = rgn
                if rgn.name:
                    self._regions[ rgn.name ] = rgn

    def region( self, rgn=0 ):
        return self._regions[ rgn ]

    def map( self, *args ):
        rgn = 0
        if type(args[0]) in (int,str):
            (rgn,*args) = args
        rgn = self.region( rgn )
        if self.parent is not None:
            (struct,) = args
            return self.parent.map( struct, rgn )
        else:
            return rgn.map( *args )

    # TODO determine if the device has any irq

    def irq_enable( self ):
        os.write( self._fd, b'\x01\x00\x00\x00' )

    def irq_disable( self ):
        os.write( self._fd, b'\x00\x00\x00\x00' )

    # note: irq is disabled once received.  you need to reenable it
    #   - before handling it, if edge-triggered
    #   - after handling it, if level-triggered
    def irq_recv( self ):
        os.read( self._fd, 4 )
