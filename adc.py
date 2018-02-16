#!/usr/bin/python3


import bitblanket as bb
import curses
from curses import wrapper
from adcdictionary import ADCList as adcDict


ADC = bb.bitBlanket("adc", 0x204, 4)

################# a generic register editor #################################
#
# Frankly it's very poorly written and needs to be, and will be, restructured
# completely using classes, and other things.
#

def main(stdscr):
    stdscr.clear()
    (maxy, maxx) = stdscr.getmaxyx()
    width = 40
    height = 4
    ncols = int((maxx-10)/width)
    nrows = (int(len(adcDict)/ncols)+1)
    pad = curses.newpad((nrows)* height,maxx)
    curses.curs_set(0)
    pad.nodelay(True)
    key = ''
    pad.keypad(True)
    keymap = {
        "KEY_LEFT":-1,
        "KEY_RIGHT":1,
        "KEY_UP":-ncols,
        "KEY_DOWN":ncols
    }
    selected = 0
    edit = -1
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    bitDepth = 0
    bitOffset = 0
    inValue = [0]*32
    while key != 'q':

        y = 0
        x = 0
        i = 0
        newValue = -1;
        try:
           key = pad.getkey()
        except:
           key = -1
        try:
            if (edit == -1):
                delta = keymap[key]
            else:
                bitOffset = bitOffset + keymap[key]
                if (bitOffset > 0):
                    bitOffset = 0
                elif (bitOffset < -(bitDepth)):
                    bitOffset = -(bitDepth)
        except:
            delta = 0
        if (key == "KEY_ENTER") or (key == "\n") or (key == "\r") or (key ==
                                                                      'c'):

            if ((edit == -1) and (key != 'c')):
                edit = selected
            elif (edit != -1):
                if (key != 'c'):
                    inValue = "".join(map(str,inValue))
                    inValue = int(inValue, 2)
                    pad.addstr(int(edit/ncols)*height+1, edit%ncols*width,
                               format(inValue, "0{0}b".format(32)))
                    ADC[adcDict[editName]] = inValue 
                pad.addstr(int(edit/ncols)*height+2,edit%ncols*width,
                          " "*32)
                edit = -1
                bitDepth = 0
                bitOffset = 0
                inValue = [0]*32
        if (key == '0') or (key =='1'):
            newValue = key
        if edit==-1:
            selected = (delta + selected) % len(adcDict)
        for name in adcDict:
            if (key == 'q'):
                break
            attr = curses.A_NORMAL
            if (i == selected):
                attr = curses.A_STANDOUT
            if (i == edit):
                attr = curses.color_pair(1)
                editName = name
            pad.addstr(y, x, name+":{0}".format(i), attr)
            pad.addstr(y+1, x, format(ADC[adcDict[name]], "0{0}b".format(32)))
            i = i + 1
            x = x + width
            if (x/width >= ncols):
                x = 0
                y = y + height
        if (edit != -1):
            curses.curs_set(1)
            pad.move(int(edit/ncols)*height+2,edit%ncols*width+bitDepth+bitOffset)
            if (newValue != -1):
                pad.addstr(newValue)
                inValue[bitDepth+bitOffset] = int(newValue)
                if (bitOffset == 0):
                    bitDepth = bitDepth + 1
                if bitDepth > 31:
                    bitDepth = 31;
        else:
            curses.curs_set(0)
        pad.refresh(0, 0, 0, 0, maxy-1, maxx-1)
wrapper(main)




#for x in ADC:
#    print (type(x) , " : " , format(x, '0{0}b'.format(8)))

#print(bin(ADC:3]))

#print(bin(ADC["REVISION"]))
