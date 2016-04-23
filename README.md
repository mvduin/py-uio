# py-uio
Userspace I/O in Python

Just a little proof-of-concept test.  Stuff in etc goes in /etc if it's not
already there; dts/l3-sn.dtsi goes into your DT (if you want to use an overlay
you need to convert it to overlay syntax); probably requires Python 3.5.

I picked the l3-sn as a target specifially since it's very fussy about access
size, making it good testing ground.  dts/adc.dtsi is a suggestion for a more
useful target.
