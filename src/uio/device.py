import os
import re
import ctypes
import struct
from os import O_RDWR, O_CLOEXEC, O_NONBLOCK
from stat import S_ISCHR
from mmap import mmap
from pathlib import Path
from ctypes import c_uint8 as ubyte
from fcntl import ioctl

PAGE_SHIFT = 12
PAGE_SIZE = 1 << PAGE_SHIFT
PAGE_MASK = -PAGE_SIZE

UIO_IOC_GET_PINCTRL_STATE = 2 << 30 | 32 << 16 | 117 << 8 | 0x40
UIO_IOC_SET_PINCTRL_STATE = 1 << 30 | 32 << 16 | 117 << 8 | 0x41

# a physical memory region associated with an uio device
class MemRegion:
    def __init__( rgn, parent, address, size, name=None, uio=None, index=None ):
        if parent == None and uio == None:
            raise ValueError( "parent region or uio device required" )
        if size < 0:
            raise ValueError( "invalid size" )

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

        # nothing to map
        if size == 0:
            return

        if parent:
            # need to use parent's mapping
            if rgn not in parent:
                raise ValueError( "memory region not inside parent" )

            offset = rgn.address - parent.address
            if offset >= parent.mappable:
                return

            rgn.mappable = min( parent.mappable - offset, size )
            rgn._mmap = parent._mmap[ offset : offset + rgn.mappable ]

        elif rgn.address & ~PAGE_MASK:
            return    # not page-aligned, can't be mapped

        else:
            # round down to integral number of pages
            rgn.mappable = size & PAGE_MASK

            # UIO uses a disgusting hack where the memory map index is
            # passed via the offset argument.  In the actual kernel call
            # the offset (and length) are in pages rather than bytes, hence
            # we actually need to pass index * PAGE_SIZE as offset.
            rgn._mmap = memoryview( mmap( rgn.uio._fd, rgn.mappable,
                                            offset = rgn.index * PAGE_SIZE ) )

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

    # fill bytes in region at given offset
    def fill( rgn, length=None, offset=0, value=0 ):
        if value not in range(256):
            raise ValueError( "invalid fill value" )
        if length is None:
            length = rgn.mappable
        # map ctypes instance (does all necessary error checking)
        mem = (ubyte * length).from_buffer( rgn._mmap, offset )
        ctypes.memset( mem, value, length )

    # write data into region at given offset
    def write( rgn, data, offset=0 ):
        data = bytes(data)
        if offset < 0 or offset > rgn.mappable:
            raise ValueError( "invalid offset" )
        end = offset + len( data )
        if offset == end:
            return
        if end > rgn.mappable:
            raise ValueError( "write extends beyond mappable area" )
        rgn._mmap[ offset : end ] = data

    # read data from region at given offset
    def read( rgn, length=None, offset=0 ):
        # read ctypes instance (does all necessary error checking)
        if isinstance( length, type ):
            return (length * 1).from_buffer_copy( rgn._mmap, offset )[0]

        # read bytes
        return bytes( rgn.map( length, offset ) )

    # map data from region at given offset
    def map( rgn, length=None, offset=0 ):
        if rgn._mmap == None:
            raise RuntimeError( "memory region cannot be mapped" )

        if isinstance( length, type ):
            # map ctypes instance (does all necessary error checking)
            return length.from_buffer( rgn._mmap, offset )

        if isinstance( length, int ) or length == None:
            # map byte-range
            if offset < 0:
                raise ValueError( "offset cannot be negative" )
            end = rgn.mappable
            if length != None:
                end = min( offset + length, end )
            if offset == 0 and end == rgn.mappable:
                return rgn._mmap
            return rgn._mmap[ offset : end ]

        raise TypeError( "first argument should be length or ctypes type" )


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


    # get/set pinctrl state
    @property
    def pinmux( self ):
        buf = ioctl( self._fd, UIO_IOC_GET_PINCTRL_STATE, bytes(32) )
        return str( buf[ 0 : buf.index(0) ], 'ascii' )

    @pinmux.setter
    def pinmux( self, value ):
        if isinstance( value, str ):
            value = bytes( value, 'ascii' )
        else:
            value = bytes( value )
        ioctl( self._fd, UIO_IOC_SET_PINCTRL_STATE, value + bytes(32) )


    # TODO determine if the device has any irq

    def irq_recv( self ):
        try:
            (counter,) = struct.unpack( "I", os.read( self._fd, 4 ) )
            return counter
        except BlockingIOError:
            return None

    def irq_control( self, value ):
        os.write( self._fd, struct.pack( "I", value ) )


    # irq control functions for uio_pdrv_genirq:

    def irq_disable( self ):
        self.irq_control( 0 )

    def irq_enable( self ):
        self.irq_control( 1 )

    # note: irq is disabled once received.  you need to reenable it
    #   - before handling it, if edge-triggered
    #   - after handling it, if level-triggered
