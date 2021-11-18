#pragma once
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
#include <limits.h>

__attribute__(( always_inline, noreturn, format( printf, 1, 2 ) ))
static inline void die( char const *fmt, ... )
{
	fprintf( stderr, fmt, __builtin_va_arg_pack() );
	exit( EXIT_FAILURE );
}


using uint = unsigned int;

using u8  = uint8_t;
using u16 = uint16_t;
using u32 = uint;
using u64 = uint64_t;

using s8  = int8_t;
using s16 = int16_t;
using s32 = int;
using s64 = int64_t;


template< typename T >
struct OutReg {
	T volatile _reg;

	void operator () ( T val ) volatile {  _reg = val;  }
};


// parse string as unsigned int in a strict way
inline uint parse_uint( char const *&p )
{
	assert( p && *p );
	uint n = 0;
	uint c = *p - '0';
	if( c == 0u ) {
		c = p[1] - '0';
		if( c > 9 )
			++p;
	} else {
		while( c <= 9 && n <= UINT_MAX / 10u && c <= ~( n * 10u ) ) {
			n = n * 10u + c;
			c = *++p - '0';
		}
	}
	return n;
}
