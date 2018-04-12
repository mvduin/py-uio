import pathlib
import os
from struct import unpack_from as unpack

class Path( pathlib.PosixPath ):
    __slots__ = ()

    def bytes( path, prop ):
        return (path/prop).read_bytes()

    def u32( path, prop ):
        return unpack( '>I', path.bytes( prop ) )[0]

    def strs( path, prop ):
        s = path.bytes( prop ).split( b'\x00' )
        if s.pop() != b'':
            raise RuntimeError("Malformed string(-array) property")
        return s

    def str( path, prop ):
        return path.strs( prop )[0]

    @property
    def phandle( path ):
        return path.u32( 'phandle' )

    def path( path, prop ):
        path = path.str( prop )
        if path[:1] != b'/':
            raise RuntimeError( "Malformed device tree path: %s" % path )
        return root / os.fsdecode( path[1:] )

root = Path( '/proc/device-tree' )
symbol = (root/'__symbols__').path
alias = (root/'aliases').path

def dt( s ):
    if type( s ) == Path:
        return s
    if isinstance( s, pathlib.Path ):
        return Path( s )
    if '/' in s:
        ( s, p ) = s.split( '/', 1 )
        return dt( s )/p
    if s == '':
        return root
    if s[0] == '&':
        return symbol( s[1:] )
    return alias( s )
