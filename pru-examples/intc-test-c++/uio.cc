#include "common.h"
#include "uio.h"
#include <unistd.h>
#include <assert.h>
#include <sys/mman.h>

static constexpr int MAX_UIO_MAPS = 5;
static constexpr size_t PAGE_SIZE = 0x1000;

u8 *uio_mmap( int fd, int index, size_t size, bool readonly )
{
	if( index < 0 || index >= MAX_UIO_MAPS )
		die( "uio_mmap(): invalid index (%d)\n", index );
	if( size == 0 || size > -PAGE_SIZE )
		die( "uio_mmap(): invalid size (0x%zx)\n", size );

	size += -size & ( PAGE_SIZE - 1 );  // round up to multiple of page size

	int prot = PROT_READ | ( readonly ? 0 : PROT_WRITE );
	void *ptr = mmap( nullptr, size, prot, MAP_SHARED, fd, index * PAGE_SIZE );
	if( ptr == MAP_FAILED )
		die( "uio_mmap(%d,%d,0x%zx,%s): %m\n", fd, index, size, readonly ? "true" : "false" );

	assert( ptr != nullptr );
	return (u8 *)ptr;
}

u8 *uio_mmap_from_env( char const *name, size_t size, size_t align, bool readonly )
{
	assert( align != 0 && ( align & ( align - 1 ) ) == 0 );

	char const *s = getenv( name );
	if( ! s || ! *s )
		die( "uio_mmap_from_env(\"%s\"): Environment variable empty or not set\n", name );
	int fd = (int)parse_uint( s );
	if( *s != ',' || ! *++s ) {
	parse_error:
		die( "uio_mmap_from_env(\"%s\"): Parse error (\"%s\")\n", name, s );
	}
	int index = (int)parse_uint( s );
	if( *s != ',' || ! *++s )
		goto parse_error;
	uint offset = parse_uint( s );
	if( *s )
		goto parse_error;

	if( fd < 3 )
		die( "uio_mmap_from_env(\"%s\"): Invalid file descriptor (%u)\n", name, fd );
	if( index < 0 || index >= MAX_UIO_MAPS )
		die( "uio_mmap_from_env(\"%s\"): Invalid mmap index (%u)\n", name, index );
	if( offset >= -size || ( offset & ( align - 1 ) ) )
		die( "uio_mmap_from_env(\"%s\"): Invalid offset (%u)\n", name, offset );

	u8 *m = uio_mmap( fd, index, offset + size, readonly );
	return m + offset;
}


PruIrq PruIrq::from_env( char const *name ) {
	char const *s = getenv( name );
	if( ! s || ! *s )
		die( "PruIrq::from_env(\"%s\"): Environment variable empty or not set\n", name );
	int fd = (int)parse_uint( s );
	if( *s != ',' || ! *++s ) {
	parse_error:
		die( "PruIrq::from_env(\"%s\"): Parse error (\"%s\")\n", name, s );
	}
	uint index = parse_uint( s );
	if( *s )
		goto parse_error;

	if( fd < 3 )
		die( "PruIrq::from_env(\"%s\"): Invalid file descriptor (%u)\n", name, fd );
	if( index < 2 || index > 9 )
		die( "PruIrq::from_env(\"%s\"): Invalid index (%u)\n", name, index );

	return { fd, (u8)index };
}
