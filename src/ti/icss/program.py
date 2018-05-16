from struct import unpack_from as unpack
from pathlib import Path
from warnings import warn

class Segment:
    def __init__( self, data, start ):
        if not isinstance( data, bytes ):
            raise TypeError()
        self.data  = data
        self.start = start

    @property
    def end( self ):
        return self.start + len( self.data )

class Memory:
    def __init__( self, name, address, size, is_code ):
        self.name = name
        self.address = address
        self.size = size
        self.is_code = is_code
        self.segments = []

    def write_into( self, rgn ):
        for seg in self.segments:
            rgn.write( seg.data, seg.start )

    def _find_insert( self, start, end ):
        ( i, prev ) = ( -1, None )
        for i, next in enumerate( self.segments ):
            if end <= next.start:
                # insert.end <= next.start
                return ( i, prev, seg )
            if start < next.end:
                raise RuntimeError( "Overlapping segments" )
            prev = next
            # prev.end <= insert.start
        return ( i + 1, prev, None )

    def add( self, data, start ):
        if start < 0 or start > self.size:
            raise RuntimeError( "Invalid segment load address" )

        data = bytes( data )
        end = start + len( data )

        if end > self.size:
            raise RuntimeError( "Segment extends beyond end of memory" )

        ( i, prev, next ) = self._find_insert( start, end )

        if prev and prev.end == start:
            # merge with previous segment
            prev.data += data
        else:
            # insert new segment
            prev = Segment( data, start )
            self.segments.insert( i, prev )
            i += 1

        if next and end == next.start:
            # merge with next segment
            prev.data += next.data
            del self.segments[ i ]

memories = [
        ( 'iram',            0x0,  0x4000, True ),
        ( 'dram',            0x0,  0x2000, False ),
        ( 'peer_dram',    0x2000,  0x2000, False ),
        ( 'shared_dram', 0x10000, 0x10000, False ),
    ]

class Program:
    def __init__( self ):
        self.path = None
        self.entrypoint = None
        self.memories = [ Memory( *meminfo ) for meminfo in memories ]

    def add_segment( self, data, address, is_code=False ):
        for mem in reversed( self.memories ):
            if address >= mem.address and is_code == mem.is_code:
                return mem.add( data, address - mem.address )
        raise RuntimeError( "Invalid segment load address" )

    @staticmethod
    def load( path, filetype=None, *, entrypoint=None ):
        path = Path( path )

        with open( path, 'rb' ) as f:
            exe = f.read()

        if filetype is None: # auto detect filetype
            # ELF magic is not a valid pru instruction (in little endian)
            if exe[:4] == b'\x7fELF':
                filetype = 'elf'
            else:
                filetype = 'bin'

        program = Program()
        program.path = path
        program.entrypoint = entrypoint

        if filetype == 'elf':
            program._load_elf( exe )
        elif filetype == 'bin':
            program._load_bin( exe )
        else:
            raise ValueError( "Unknown filetype: %r" % filetype )

        return program

    def _load_bin( self, exe ):
        if self.entrypoint is None:
            self.entrypoint = 0

        self.add_segment( exe, 0, is_code=True )

        # try to load debug information
        path = self.path.with_suffix( '.dbg' )
        try:
            with open( path, 'rb' ) as f:
                dbg = f.read()
        except FileNotFoundError:
            return

        # TODO parse debug data


    def _load_elf( self, exe ):
        # parse file header
        if exe[:7] != b'\x7fELF\x01\x01\x01':
            raise RuntimeError( "Invalid ELF32 header" )
        if unpack( 'HH', exe, 0x10 ) != ( 2, 144 ):
            raise RuntimeError( "Not a TI-PRU executable" )
        ( entry, phoff, phsz, nph ) = unpack( 'II10xHH', exe, 0x18 )

        if self.entrypoint is None:
            if entry & 3:
                raise RuntimeError( "Entrypoint not word-aligned: 0x%x" % entry )
            self.entrypoint = entry >> 2
        elif entry != self.entrypoint << 2:
            warn( "Overriding entrypoint of ELF executable" )

        for i in range( nph ):
            ( pt, *args ) = unpack( '8I', exe, phoff )
            phoff += phsz

            if pt == 1:
                self._load_elf_segment( exe, *args )
            elif pt == 0x70000000:
                pass  # segment attributes
            else:
                warn( "Unknown program header type: 0x%x" % pt )

    def _load_elf_segment( self, exe, offset, va, pa, fsz, msz, flags, align ):
        if fsz > msz or offset + fsz > len( exe ):
            raise RuntimeError( "Invalid segment" )

        if not ( flags & 1 ):
            # data segment
            self.add_segment( exe[ offset : offset + fsz ], va )
            self.add_segment( bytearray( msz - fsz ), va + fsz )
        else:
            # code segment
            if va & 3 or fsz & 3 or msz & 3:
                raise RuntimeError( "Misaligned code segment" )
            if fsz < msz:
                raise RuntimeError( "Uninitialized code segment" )
            self.add_segment( exe[ offset : offset + fsz ], va, is_code=True )
