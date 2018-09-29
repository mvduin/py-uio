export SHELLOPTS := pipefail

CPP = cpp
CPPFLAGS = -nostdinc -undef -x assembler-with-cpp
CPPFLAGS += -D__DTS__
CPPFLAGS += -I include
DTC = dtc

overlays := $(patsubst %.dtsi,%.dtbo,$(wildcard *.dtsi))

# beagleboard-x15 doesn't use overlays
overlays := $(filter-out dra7-% bbx15-%,${overlays})

all :: ${overlays}

clean ::
	${RM} *.dtbo

%.dtbo: %.dtsi
	${CPP} ${CPPFLAGS} $< -pipe | bin/dtsi-to-overlay \
		| ${DTC} -@ -q -I dts -O dtb ${OUTPUT_OPTION}

.DELETE_ON_ERROR:
