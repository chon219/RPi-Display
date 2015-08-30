# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import spidev
import time
import sys
from bdflib import reader
from commands import *

WIDTH = 128
HEIGHT = 64

class Display:
    def __init__(self, dc = 15, rst = 13, fontpath = "./wenquanyi_12pt.bdf"):
        self.DC = dc
        self.RST = rst
        self.fontpath = fontpath
        self.buff = [([0x00] * WIDTH)] * (HEIGHT/8)
        try:
            self.setup()
        except Exception:
            self.cleanup()

    def setup(self):
        self.setup_spi()
        self.setup_gpio()
        self.setup_display()
        self.setup_font()

    def setup_spi(self):
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)

    def setup_gpio(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.DC, GPIO.OUT)
        GPIO.setup(self.RST, GPIO.OUT)

    def setup_display(self):
        GPIO.output(self.RST, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.RST, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(self.RST, GPIO.HIGH)
        self.command(DISPLAYOFF);
        self.command(SETDISPLAYCLOCKDIV)
        self.command(0x80)
        self.command(SETMULTIPLEX)
        self.command(0x3f)
        self.command(SETDISPLAYOFFSET)
        self.command(0x0)
        self.command(SETSTARTLINE | 0x0)
        self.command(CHARGEPUMP)
        self.command(0x14)
        self.command(MEMORYMODE)
        self.command(0x00)
        self.command(SEGREMAP | 0x1)
        self.command(COMSCANDEC)
        self.command(SETCOMPINS)
        self.command(0x12)
        self.command(SETCONTRAST)
        self.command(0xcf)
        self.command(SETPRECHARGE)
        self.command(0xf1)
        self.command(SETVCOMDETECT)
        self.command(0x40)
        self.command(DISPLAYALLON_RESUME)
        self.command(NORMALDISPLAY)
        self.command(DISPLAYON)

    def setup_font(self):
        f = open(self.fontpath)
        content = f.readlines()
        f.close()
        self.font = reader.read_bdf(iter(content))

    def cleanup(self):
        self.cleanup_gpio()
        self.cleanup_spi()

    def cleanup_gpio(self):
        GPIO.cleanup()

    def cleanup_spi(self):
        self.spi.close()

    def command(self, c):
        GPIO.output(self.DC, GPIO.LOW)
        self.spi.writebytes([c])

    def data(self, c):
        GPIO.output(self.DC, GPIO.HIGH)
        if type(c) is not list:
            self.spi.writebytes([c])
        else:
            self.spi.writebytes(c)

    def display(self):
        self.command(SETLOWCOLUMN | 0x0)
        self.command(SETHIGHCOLUMN | 0x0)
        self.command(SETSTARTLINE | 0x0)
        for line in self.buff:
            self.data(line)

    def clear(self):
        self.buff = [([0x00] * WIDTH)] * (HEIGHT/8)
        self.display()

    def invert(self, i):
        if i:
            self.command(INVERTDISPLAY)
        else:
            self.command(NORMALDISPLAY)

    def __getfontbitmap(self, c):
        char = self.font.glyphs_by_codepoint.get(ord(c))
        if not char:
            return None
        lines = char.data[::-1]
        pos_x, pos_y, width, height = char.get_bounding_box()
        advance = char.advance
        if height < 16:
            lines = lines + [0]*(pos_y+3)
            if (len(lines)) < 16:
                lines = [0]*(16-len(lines)) + lines
            else:
                lines = lines[-16:]
            height = 16
        if width < advance:
            for i in xrange(len(lines)):
                lines[i] = lines[i]<<(advance-width)
            width = advance
        bmp_1 = []
        for i in xrange(width):
            t = 0x00
            for j in xrange(height/2-1, -1, -1):
                t = t<<0x01
                t += (lines[j]>>(width-i-1))&0x01
            bmp_1.append(t)
        bmp_2 = []
        for i in xrange(width):
            t = 0x00
            for j in xrange(height-1, height/2-1, -1):
                t = t<<0x01
                t += (lines[j]>>(width-i-1))&0x01
            bmp_2.append(t)
        return [bmp_1, bmp_2]

    def __formatParams(self, x, y, n, s):
        x = int(x) if type(x)!=int else x
        y = int(y) if type(y)!=int else y
        n = int(n) if type(n)!=int else n
        s = s.decode('utf-8') if type(s)!=unicode else s
        return (x, y, n, s)

    def __validateParams(self, x = 0, y = 0, n = 1, s = u""):
        if x > WIDTH or x < 0 or type(x)!=int:
            return False
        if y > (HEIGHT/8-2) or y < 0 or type(y)!=int:
            return False
        if (2*n+y) > (HEIGHT/8) or n < 1 or type(n)!=int:
            return False
        if type(s) != unicode:
            return False
        return True

    def __fillLine(self, y, line):
        if len(line) < WIDTH:
            line.extend([0x00] * (WIDTH-len(line)))
        else:
            line = line[0:WIDTH]
        self.buff[y] = line

    def __fillLines(self, y, lines):
        n = y
        for line in lines:
            self.__fillLine(n, line)
            n += 1

    def __clearLine(self, y, data):
        self.__fillLine(y, [data]*WIDTH)

    def __clearLines(self, y, n, data):
        self.__fillLines(y, [[data]*WIDTH]*(n*2))

    def displayText(self, x, y, n, s):
        x, y, n, s = self.__formatParams(x, y, n, s)
        if not self.__validateParams(x, y, n, s):
            raise Exception("Invalid parameters.")
        self.__clearLines(y, n, 0x00)
        length = x
        line1 = [0x00] * length
        line2 = [0x00] * length
        for c in s:
            bmp = self.__getfontbitmap(c)
            if bmp:
                if (length+len(bmp[0])) > WIDTH:
                    if n > 1:
                        self.__fillLines(y, [line1, line2])
                        length = 0
                        line1 = []
                        line2 = []
                        n = n - 1
                        y = y + 2
                    else:
                        break
                line1.extend(bmp[0])
                line2.extend(bmp[1])
                length += len(bmp[0])
            else:
                continue
        self.__fillLines(y, [line1, line2])
        self.display()
