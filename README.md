# py-uio
Userspace I/O in Python

All examples currently target the BeagleBone Black.

Copy the stuff in the [etc/](etc/) dir to the corresponding places in `/etc`
and tweak the udev rule to taste (user/group/permissions).

The [dts/](dts/) dir contains example device tree fragments.  If you use a
custom dts then you can simply include such dtsi files, but since most people
don't you can also type `make` to build device tree overlays from them and use
the utils in [dts/bin/](dts/bin/) to add/remove them.

Example 1 (gpio-triggered IRQ):
```bash
cd dts
make p9.12-irq.dtbo
sudo bin/add-overlay p9.12-irq.dtbo
cd ..
./p9.12-irq.py
# now pull P9.12 to ground to trigger the irq the script is waiting for
```

Example 2 (small experiment with L3 service network):
```bash
cd dts
make l3-sn.dtbo
sudo bin/add-overlay l3-sn.dtbo
cd ..
./l3-sn-test.py
```

The l3-sn is useful testing ground since it is very fussy about access size.
