#pragma once
#include <stddef.h>
#include "common.h"

struct alignas(0x2000) PruIntc {
	using ev_t = s32;	// event number (range 0..63)
	// negative value for ev_t is used to indicate no event is pending.

	using ch_t = u8;	// channel number (range 0..9)
	using out_t = u8;	// irq output number (range 0..9)


/*000*/	u32 ident;	//r-
	// subarctic 2.1 pruss -- 4'e82'a9'00

/*004*/	u32 config;
	// bit   0	z-
	// bit   1	z-
	// bits  2- 3	rw  nesting mode:
	//			0 = disabled (no nesting)
	//			1 = automatic, per output
	//			2 = automatic, global
	//			3 = manual
	// bit   4	rw  event holding enabled
	// bits  5-31	z-

alignas(0x10)
/*010*/	u32 enabled;
	// bit   0	rw  when clear, all outputs are masked
	// bits  1-31	z-

/*014*/	u32 _014;
/*018*/	u32 _018;

/*01c*/	u32 nesting;
	// bits  0- 8	r-/rw  global nesting level
	// bits  9-30	z-
	// bit  31	-x  allow write even if automatic nesting is used


	using ev_cmd_t = OutReg< ev_t >;

/*020*/	ev_cmd_t ev_set_one;
/*024*/	ev_cmd_t ev_clear_one;
/*028*/	ev_cmd_t ev_enable_one;
/*02c*/	ev_cmd_t ev_disable_one;

/*030*/	u32 _wakeup_en;

	using out_cmd_t alignas(4) = OutReg< out_t >;

/*034*/	out_cmd_t out_enable_one;
/*038*/	out_cmd_t out_disable_one;

alignas(0x80)
/*080*/	ev_t volatile cur_event;  //r-  global highest-priority event

	// FIXME
	using ev_set_t alignas(1024/8) = u64;

	// FIXME
alignas(0x200)
/*200*/	ev_set_t volatile _ev_set;
/*280*/	ev_set_t volatile _ev_clear;
/*300*/	ev_set_t volatile _ev_enable;
/*380*/	ev_set_t volatile _ev_disable;

alignas(0x80)
/*400*/	ch_t  ev_ch[ 1024 ];	//rw  event -> channel  map
/*800*/	out_t ch_out[ 256 ];	//rw  channel -> output  map

/*900*/	ev_t  volatile out_cur_event[ 256 ];  //r-  highest-priority event per output

/*d00*/	ev_set_t ev_polarity;	//rw
/*d80*/	ev_set_t ev_edgedet;	//rw

alignas(0x80)
/*e00*/	u32 _0e00[ ( 0x1100 - 0xe00 )/4 ];

/*100*/	u32 out_nesting[ 256 ]; // per-output nesting, same format as global nesting register

/*500*/	u32 volatile out_enabled;
};

static_assert( offsetof( PruIntc, out_enabled ) == 0x1500 );
