# utilities to access Device Tree properties

import pathlib
import os

class DtNode( pathlib.PosixPath ):
    __slots__ = ()

    @property
    def phandle( node ):
        return node.u32( 'phandle' )

    def bytes( node, prop ):
        return (node/prop).read_bytes()

    def u32( node, prop ):
        return unpack( '>I', node.bytes( prop ) )[0]

    def strs( node, prop ):
        s = node.bytes( prop ).split( b'\x00' )
        if s.pop() != b'':
            raise RuntimeError("Malformed string(-array) property")
        return s

    def str( node, prop ):
        return node.strs( prop )[0]

    def path( node, prop ):
        node = node.str( prop )
        if node[:1] != b'/':
            raise RuntimeError( "Malformed device tree node: %s" % node )
        return dt_root / os.fsdecode( node[1:] )

dt_root = DtNode( '/proc/device-tree' )
dt_symbol = (dt_root/'__symbols__').path
dt_alias = (dt_root/'aliases').path

def dt( s ):
    if type( s ) == DtNode:
        return s
    if isinstance( s, pathlib.Path ):
        return DtNode( s )
    if '/' in s:
        ( s, p ) = s.split( '/', 1 )
        return dt( s )/p
    if s == '':
        return dt_root
    if s[0] == '&':
        return dt_symbol( s[1:] )
    return dt_alias( s )



# utilities to fix some annoying ctypes behaviour

function = type( lambda: () )

from ctypes import c_uint8 as ubyte
import ctypes

class cached_getter:
    __slots__ = ('__name__', 'desc',)

    def __init__( self, desc, name=None ):
        if name is None:
            name = desc.__name__
        self.__name__ = name
        self.desc = desc

    def __get__( self, instance, owner ):
        if not isinstance( self.desc, function ):
            value = self.desc.__get__( instance, owner )
            if instance is not None:
                instance.__dict__[ self.__name__ ] = value
            return value
        elif instance is not None:
            value = self.desc( instance )
            instance.__dict__[ self.__name__ ] = value
            return value
        else:
            return self

def fix_ctypes_struct( cls ):
    instance = cls()
    const_fields = []
    if hasattr( cls, '_const_' ):
        const_fields = cls._const_
    for name, ctype, *args in cls._fields_:
        if name == "":
            continue
        desc = cls.__dict__[ name ]
        if name not in const_fields:
            if len(args) > 0:
                continue
            if not isinstance( desc.__get__( instance, cls ), ctype ):
                continue
        setattr( cls, name, cached_getter( desc, name ) )
    return cls

def struct_field( offset, ctype, name='field' ):
    @fix_ctypes_struct
    class Struct( ctypes.Structure ):
        _fields_ = [ ("", ubyte * offset), (name, ctype) ]
    return getattr( Struct, name )

def struct_bitfield( offset, ctype, start, width, name='field' ):
    size = ctypes.sizeof( ctype ) * 8
    assert start in range( 0, size )
    assert width in range( 1, size - start + 1 )

    @fix_ctypes_struct
    class Struct( ctypes.Structure ):
        _fields_ = [ ("", ubyte * offset), (name, ctype, width) ]
        if start != 0:
            _fields_.insert( 1, ("", ctype, start) )
    return getattr( Struct, name )

def add_field( Struct, name, offset, ctype, bitfield_start=None, bitfield_width=None ):
    assert not hasattr( Struct, name )
    assert offset in range( 0, ctypes.sizeof( Struct ) - ctypes.sizeof( ctype ) + 1 )

    if bitfield_start is None and bitfield_width is None:
        field = struct_field( offset, ctype, name )
    else:
        field = struct_bitfield( offset, ctype, bitfield_start, bitfield_width, name )
    setattr( Struct, name, field )
