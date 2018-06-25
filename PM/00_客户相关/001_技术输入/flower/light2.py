import neopixel
#import machine

np = neopixel.NeoPixel(machine.Pin(2), 256)
for i in range(256):
    np[i] = (i//16, 0, 0)
np.write()