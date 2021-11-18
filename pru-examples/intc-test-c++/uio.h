#pragma once
#include "common.h"
#include <unistd.h>
#include <assert.h>
#include <type_traits>

inline void uio_wfi( int fd )
{
	uint counter;
	auto n = read( fd, &counter, sizeof counter );
	if( n < 0 ) {
		die( "uio_wfi(%d): read(): %m\n", fd );
	} else {
        	assert( (size_t)n == sizeof counter );
	}
}


u8 *uio_mmap( int fd, int index, size_t size, bool readonly );
u8 *uio_mmap_from_env( char const *name, size_t size, size_t align, bool readonly );

template< typename T >
inline T &uio_mmap_from_env( char const *name )
{
	return *(T *)uio_mmap_from_env( name, sizeof(T), alignof(T), std::is_const_v<T> );
}


struct PruIrq {
	int fd;
	u8 index;  // pruss intc output (2..9)

	static PruIrq from_env( char const *name );
};
