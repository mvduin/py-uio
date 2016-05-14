#!/usr/bin/python3


import bitblanket as bb
import curses
from curses import wrapper
from adcdictionary import adcDict

ADC = bb.bitBlanket("adc", 0x204, adcDict)

def main(stdscr):
    stdscr.clear()
    (maxy, maxx) = stdscr.getmaxyx()
    nrows = (round(len(adcDict)/8)+1)
    width = 25
    height = 5
    pad = curses.newpad((nrows + 1)* height, 200)
    y = 0 
    x = 0
    for name in adcDict:
        pad.addstr(y, x, name)
        x = x + width
        if (x > 175):
            x = 1
            y = y + height
    pad.refresh(0, 0, 2, 2, maxy, maxx)


    while pad.getkey() is not 'q':
        pass
wrapper(main)




#for x in ADC:
#    print (type(x) , " : " , format(x, '0{0}b'.format(8)))

#print(bin(ADC[0:3]))

#print(bin(ADC["REVISION"]))
