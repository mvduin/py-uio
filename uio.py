import os
import re
from os import O_RDWR, O_CLOEXEC, O_NONBLOCK
from stat import S_ISCHR
from mmap import mmap
from pathlib import Path

class UioMap:
    def __init__( self, info ):
        self.index = int( re.fullmatch( r'map([0-9])', info.name ).group(1) )
        self.name = (info/'name').read_text().rstrip()
        self.address = int( (info/'addr').read_text(), 0 )
        self.size = int( (info/'size').read_text(), 0 )
        self._mmap = None
        self._mem = None

class Uio:
    def fileno( self ):
        return self._fd

    def __init__( self, path, blocking = True ):
        flags = O_RDWR | O_CLOEXEC
        if not blocking:
            flags |= O_NONBLOCK # for irq_recv
        path = Path( '/dev/uio', path )
        self._fd = os.open( path.path, flags )

        # build path to sysfs dir for obtaining metadata
        dev = os.stat( self._fd ).st_rdev
        dev = '{0}:{1}'.format( os.major(dev), os.minor(dev) )
        self.syspath = Path('/sys/dev/char')/dev;

        # enumerate memory mappings
        self._mappings = {}
        mapinfo = self.syspath/'maps';
        if mapinfo.is_dir():
            for m in map( UioMap, mapinfo.iterdir() ):
                self._mappings[ m.index ] = m
                self._mappings[ m.name ] = m

    # I return a memoryview since mmap doesn't allow creating writeable slices,
    # but note that slicing the mmap object itself does do the Right Thing with 
    # regard to access size, e.g. m[0:4] will perform a 32-bit access instead of
    # four byte-accesses.  With memoryview objects you have to use .cast to the
    # right type, so I'm not really happy with either solution yet.
    def map( self, m=0, offset=None, size=None ):
        m = self._mappings[ m ]

        if m._mem is None:
            m._mmap = mmap( self._fd, m.size, offset = m.index << 12 )
            m._mem = memoryview( m._mmap )

        if size is None:
            if offset is None:
                return m._mmap
            if offset == 0:
                return m._mem
            return m._mem[offset:]
        return m._mem[offset:offset+size]

    def irq_enable( self ):
        os.write( self._fd, b'\x01\x00\x00\x00' )

    def irq_disable( self ):
        os.write( self._fd, b'\x00\x00\x00\x00' )

    # note: irq is disabled once received.  you need to reenable it
    #   - before handling it, if edge-triggered
    #   - after handling it, if level-triggered
    def irq_recv( self ):
        os.read( self._fd, 4 )
