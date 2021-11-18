#include "common.h"
#include "pruss-intc.h"
#include "uio.h"
#include <stdio.h>

void handle_event( int ev )
{
	printf( "event %d\n", ev );
}

void handle_events( PruIntc &intc, PruIrq const &irq )
{
	int ev = intc.out_cur_event[ irq.index ];
	if( ev < 0 ) {
		fprintf( stderr, "spurious interrupt\n" );
		return;
	}

	do {
		intc.ev_clear_one( ev );
		handle_event( ev );
		ev = intc.out_cur_event[ irq.index ];
	} while( ev >= 0 );
}

int main( int argc, char *argv[] )
{
	if( argc != 1 )
		die( "Unexpected argument: %s\n", argv[1] );

	if( ! getenv( "uio:mem:pruss-intc" ) || ! getenv( "uio-pruss:irq:test" ) )
		die( "This program is meant to be executed by intc-test-c++.py\n" );

	PruIrq irq = PruIrq::from_env( "uio-pruss:irq:test" );

	PruIntc &intc = uio_mmap_from_env<PruIntc>( "uio:mem:pruss-intc" );

	setlinebuf( stdout );

	for(;;) {
		intc.out_enable_one( irq.index );

		uio_wfi( irq.fd );

		handle_events( intc, irq );
	}

	return 0;
}
