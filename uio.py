import os
import re
from os import O_RDWR, O_CLOEXEC, O_NONBLOCK
from stat import S_ISCHR
from mmap import mmap
from pathlib import Path
from ctypes import sizeof

PAGE_SHIFT = 12
PAGE_SIZE = 1 << PAGE_SHIFT
PAGE_MASK = -PAGE_SIZE

# a physical memory region associated with an uio device
class MemRegion:
    def __init__( rgn, parent, address, size, name=None, uio=None, index=None ):
        if parent == None and uio == None:
            raise RuntimeError( "parent region or uio device required" )

        # parent memory region (if any)
        rgn.parent = parent

        # physical address range
        rgn.address = address
        rgn.size = size
        rgn.end = address + size

        # identification
        rgn.name = name
        rgn.uio = uio
        rgn.index = index

        # memory mapping
        rgn.mappable = 0
        rgn._mmap = None
        rgn._offset = 0

        # nothing to map
        if size <= 0:
            return

        if parent:
            # need to use parent's mapping
            if rgn not in parent:
                raise RuntimeError( "memory region outside parent" )

            offset = rgn.address - parent.address
            if offset >= parent.mappable:
                return

            rgn.mappable = min( parent.mappable - offset, size )
            rgn._mmap = parent._mmap
            rgn._offset = parent._offset + offset

        elif rgn.address & ~PAGE_MASK:
            return    # not page-aligned, can't be mapped

        else:
            # round down to integral number of pages
            rgn.mappable = rgn.size & PAGE_MASK

            # UIO uses a disgusting hack where the memory map index is
            # passed via the offset argument.  In the actual kernel call
            # the offset (and length) are in pages rather than bytes, hence
            # we actually need to pass index * PAGE_SIZE as offset.
            rgn._mmap = mmap( rgn.uio._fd, rgn.mappable,
                            offset = rgn.index * PAGE_SIZE )

    @classmethod
    def from_sysfs( cls, uio, info, parent=None ):
        index = int( re.fullmatch( r'map([0-9])', info.name ).group(1) )

        def getinfo( attr ):
            with (info/attr).open() as f:
                return f.readline().rstrip()

        # If no name has been supplied, the region gets an auto-generated name
        # containing the full DT path.  These are useless, ignore them.
        name = getinfo( 'name' )
        if name == '' or name[0] == '/':
            name = None

        # get memory region bounds
        address = int( getinfo('addr'), 0 )
        size = int( getinfo('size'), 0 )

        return MemRegion( parent, address, size, name, uio, index )

    def subregion( rgn, offset, size, name=None ):
        return MemRegion( rgn, rgn.address + offset, size, name )

    def __contains__( rgn, child ):
        return child.address >= rgn.address and child.end <= rgn.end

    # write data into region
    def write( rgn, data, offset=0 ):
        data = bytes(data)
        if offset + len(data) > rgn.mappable:
            raise RuntimeError( "write extends beyond mappable area" )
        offset += rgn._offset
        rgn._mmap[ offset : offset + len(data) ] = data

    # read data from a region
    def read( rgn, length, offset=0 ):
        if offset + length > rgn.mappable:
            raise RuntimeError( "read extends beyond mappable area" )
        offset += rgn._offset
        return rgn._mmap[ offset : offset + length ]

    # map a struct at given offset within this memory region
    def map( rgn, struct, offset=0 ):
        if offset + sizeof(struct) > rgn.mappable:
            raise RuntimeError( "region is not mappable" )

        return struct.from_buffer( rgn._mmap, rgn._offset + offset )


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

        # check parent memory region (if any)
        if parent is not None:
            if isinstance( parent, Uio ):
                parent = parent.region()
            elif isinstance( parent, MemRegion ):
                raise TypeError

        # build path to sysfs dir for obtaining metadata
        dev = os.stat( self._fd ).st_rdev
        dev = '{0}:{1}'.format( os.major(dev), os.minor(dev) )
        self.syspath = Path('/sys/dev/char', dev).resolve()

        # enumerate memory regions
        # beware that if there are none, the dir is absent rather than empty
        self._regions = {}
        rgninfo = self.syspath/'maps'
        if rgninfo.is_dir():
            for info in rgninfo.iterdir():
                rgn = MemRegion.from_sysfs( self, info, parent )

                # allow lookup by index or (if available) by name
                self._regions[ rgn.index ] = rgn
                if rgn.name:
                    self._regions[ rgn.name ] = rgn

    def region( self, rgn=0 ):
        return self._regions[ rgn ]

    # shortcut to make subregion of default region (index 0)
    def subregion( self, offset, size, name=None ):
        return self.region().subregion( offset, size, name )

    # shortcut to map default region (index 0)
    def map( self, struct, offset=0 ):
        return self.region().map( struct, offset )


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
