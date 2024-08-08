#!/usr/bin/python3

# Probably for GPIO only for now, stop using PWM for this script!

from time import sleep
import os
from pathlib import Path

#Direction_One = Path('/dev/gpio/P8_11/direction')
#Direction_Two = Path('/dev/gpio/P8_12/direction')
#Disable_Three = Path('/dev/gpio/P9_11/direction')

class PWM:
    def __init__( self, pwm, rw=None):
        if type(pwm) is int:
            # gpio number
            self.path = '/dev/beagle/pwm/' + str(enable)
        else:
            # gpio name or path
            self.path = os.path.join('/dev/beagle/pwm/', enable)

        if rw is not None and type(rw) is not bool:
            raise TypeError()

        if rw:
            self._f = open(self.path + str(enable), 'r+b', buffering=0)
        else:
            self._f = open(self.path + enable, 'rb', buffering=0)
        self.rw = rw

    @property
    def value( self ):
        return (b'1',b'0').index(os.pread(self._f.fileno(), 1, 0))

    @value.setter
    def value(self, enable):
        if self.rw is None:
            self._f = open( self.path + 'enable', 'r+b', buffering=0)
            self.rw = True

        self._f.write( (b'1',b'0')[enable])

'''
    @property
    def direction( self ):
        return (b'1', b'0').index( os.pread( self._f.fileno(), 1, 0 ) )

    @direction.setter
    def direction( self, direction ):
        if self.rw is None:
            self._f = open( self.path + 'direction', 'r+b', buffering=0 )
            self.rw = True

        self._f.write( (b'1', b'0')[ direction ] )
'''
tora_Two = PWM.value

try:
    while True:
        tora = int(input("What integer can you think about now and please type it!"))
        if tora == 0:
            tora_Two(P8_13=1)
            sleep(2)
        else:
            tora_Two(P8_13=0)
            sleep(2)

except KeyboardInterrupt:
    pass
    print("Over and done! ")
