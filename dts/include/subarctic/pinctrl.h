#pragma once

// pinctrl-single data
#define PIN_CONFIG(i,m)	( (i) * 4 ) ( m )

// config options
#define PULL_DOWN	( 0 << 3 )
#define NO_PULL		( 1 << 3 )
#define PULL_UP		( 2 << 3 )
#define INPUT_DIS	( 0 << 5 )
#define INPUT_EN	( 1 << 5 )
#define SLEW_FAST	( 0 << 6 )
#define SLEW_SLOW	( 1 << 6 )


#define PIN_OUT_NOPULL(i,m)	PIN_CONFIG( i, m | INPUT_DIS | NO_PULL )
#define PIN_OUT_PULLDOWN(i,m)	PIN_CONFIG( i, m | INPUT_DIS | PULL_DOWN )
#define PIN_OUT_PULLUP(i,m)	PIN_CONFIG( i, m | INPUT_DIS | PULL_UP )

#define PIN_IO_NOPULL(i,m)	PIN_CONFIG( i, m | INPUT_EN | NO_PULL )
#define PIN_IO_PULLDOWN(i,m)	PIN_CONFIG( i, m | INPUT_EN | PULL_DOWN )
#define PIN_IO_PULLUP(i,m)	PIN_CONFIG( i, m | INPUT_EN | PULL_UP )

#define PIN_IN_NOPULL(i,m)	PIN_IO_NOPULL( i, m )
#define PIN_IN_PULLDOWN(i,m)	PIN_IO_PULLDOWN( i, m )
#define PIN_IN_PULLUP(i,m)	PIN_IO_PULLUP( i, m )


#define PIN_GPOUT_NOPULL(i)	PIN_OUT_NOPULL( i, 7 )
#define PIN_GPOUT_PULLDOWN(i)	PIN_OUT_PULLDOWN( i, 7 )
#define PIN_GPOUT_PULLUP(i)	PIN_OUT_PULLUP( i, 7 )

#define PIN_GPIO_NOPULL(i)	PIN_IO_NOPULL( i, 7 )
#define PIN_GPIO_PULLDOWN(i)	PIN_IO_PULLDOWN( i, 7 )
#define PIN_GPIO_PULLUP(i)	PIN_IO_PULLUP( i, 7 )

#define PIN_GPIN_NOPULL(i)	PIN_IN_NOPULL( i, 7 )
#define PIN_GPIN_PULLDOWN(i)	PIN_IN_PULLDOWN( i, 7 )
#define PIN_GPIN_PULLUP(i)	PIN_IN_PULLUP( i, 7 )
