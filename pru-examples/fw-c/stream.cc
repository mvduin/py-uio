#include <stdint.h>
#include <stddef.h>

struct Message {
	uint32_t id;
};

// layout of shared ddr3 memory (filled in by loader)
struct DDRLayout {
	Message volatile *msgbuf;
	uint16_t num_msgs;
};

struct SharedVars {
	// set by pru before halting
	char const *abort_file;
	int abort_line;

	// read-pointer updated by python
	uint16_t ridx;
};

far struct DDRLayout ddr __attribute__((location(0x10000))) = {};
far struct SharedVars volatile shmem __attribute__((location(0x10100))) = {};


// for easier debugging, record where in the source code we halted

__attribute__((noreturn))
void abort_at( char const *file, int line )
{
	shmem.abort_file = file;
	shmem.abort_line = line;
	for(;;) __halt();
}

static inline void assert_at( bool cond, char const *file, int line )
{
	if( ! cond )
		abort_at( file, line );
}

#define abort() abort_at( __FILE__, __LINE__ )
#define assert(cond) assert_at( (cond), __FILE__, __LINE__ )


// local copy of write-pointer
static uint16_t widx = 0;

// global var for write-pointer is located right after message ringbuffer
#define ddr_msgbuf_end	( ddr.msgbuf + ddr.num_msgs )
#define ddr_widx	( *(uint16_t volatile *)ddr_msgbuf_end )

void initialize()
{
	// perform sanity-checking
	assert( 0x80000000 <= (uint32_t)ddr.msgbuf );
	assert( ddr.msgbuf < ddr_msgbuf_end );

	assert( ddr_widx == widx );
	assert( shmem.ridx == widx );
}

static inline uint16_t next_idx( uint16_t idx )
{
	if( ++idx == ddr.num_msgs )
		idx = 0;
	return idx;
}

void send_message( uint32_t id )
{
	uint16_t next_widx = next_idx( widx );

	if( next_widx == shmem.ridx ) {
		// can't send message, ringbuffer is full
		abort();
	}

	Message volatile *msg = &ddr.msgbuf[ widx ];

	// fill in contents of message
	msg->id = id;

	// update write-pointer
	ddr_widx = widx = next_widx;
}

void main() {
	initialize();

	uint32_t id = 0;
	for(;;) {
		send_message( ++id );
		__delay_cycles( 100000 );
	}
}
