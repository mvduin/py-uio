# py-uio
Userspace I/O in Python

All examples currently target the BeagleBone family of devices.

This library and its examples are for interfacing with uio devices, in
particular those using the `uio_pdrv_genirq` driver and those using the
`uio_pruss` driver.

There isn't much documentation yet other than this README, but a little bit can
be found on [the wiki](https://github.com/mvduin/py-uio/wiki).

## uio_pruss

Make sure the your `/boot/uEnv.txt` enables uio-pruss by setting
`uboot_overlay_pru=/lib/firmware/AM335X-PRU-UIO-00A0.dtbo`

Copy the [uio-pruss.rules](etc/udev/rules.d/uio-pruss.rules) file to
`/etc/udev/rules.d/` and reboot.  This creates symlinks (in `/dev/uio/pruss/`) to
allow the uio-pruss devices to be located easily.

Now you can try out the various [pru-examples](pru-examples/):
 * [test.py](pru-examples/test.py) is a minimalistic example that initializes register R0 of a pru core to 123, loads and executes a [tiny pru program](pru-examples/fw/test.pasm) that increments R0, and then reads back and prints R0 (which should therefore print 124).
 * [ddr-ping.py](pru-examples/ddr-ping.py) is a small test of using a shared DDR3 memory region.
 * [elf-test.py](pru-examples/elf-test.py) demonstrates how to load an ELF executable produced by clpru.
 * [intc-test.py](pru-examples/intc-test.py) is a more involved example that showcases sharing a data structure (in pruss local memory) between python code and the PRU cores, and sending events from both pru cores via the pruss interrupt controller to event handlers in python.
 * [intc-test-asyncio.py](pru-examples/intc-test-asyncio.py) is an [asyncio](https://docs.python.org/3/library/asyncio.html) version of the same example.

To recompile the [assembly examples](pru-examples/fw/) you will need pasm, which you can just compile from source:
```bash
git clone https://github.com/beagleboard/am335x_pru_package
cd am335x_pru_package/pru_sw/utils/pasm_source
./linuxbuild
sudo cp ../pasm /usr/local/bin/
```

To recompile the [C example](pru-examples/fw-c/) you need the "TI PRU Code Generation Tools", which you can install using `sudo apt-get install ti-pru-cgt-installer`, or you can download it [here](http://software-dl.ti.com/codegen/non-esd/downloads/download.htm#PRU).

## uio_pdrv_genirq

(TODO: this is outdated information and needs to be revised!)

Copy the stuff in the [etc/](etc/) dir to the corresponding places in `/etc`
and tweak the udev rule to taste (user/group/permissions).

The [dts/](dts/) dir contains example device tree fragments.  If you use a
custom dts then you can simply include such dtsi files, but since most people
don't you can also type `make` to build device tree overlays from them and use
the utils in [dts/bin/](dts/bin/) to add/remove them.

Example 1 (gpio-triggered IRQ):
```bash
cd dts
make gpio-irq.dtbo
sudo bin/add-overlay gpio-irq.dtbo
cd ..
./gpio-irq.py
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
