# py-uio
Userspace I/O in Python

All examples current target the BeagleBone Black.

Copy the stuff in the [etc/](etc/) dir to the corresponding places in `/etc` and tweak
the udev rule to taste (user/group/permissions).

The [dts/](dts/) dir contains example device tree fragments.  If you use a custom dts
then you can simply include such dtsi files, but since most people don't you
can also type `make` to build device tree overlays from them and use the utils
in [dts/bin/](dts/bin/) to add/remove them.

Example:
```bash
cd dts
make p9.12-irq.dtbo
sudo bin/add-overlay p9.12-irq.dtbo
cd ..
./p9.12-irq.py
# now pull P9.12 to ground to trigger the irq the script is waiting for
```

There's also a little example targeting the l3-sn since it is unusually fussy
about access size, making it good testing ground.

## Known issues

The code may require Python 3.5 currently, I'll work on at least reducing that
to Python 3.4.

Overlays aren't working yet for me currently, they seem to install fine but an
error appears in the kernel log and the uio device never appears.  This may be
kernel version dependent, haven't explored yet.
