pasm_sources := $(wildcard *.pasm)
pasm_binaries := ${pasm_sources:%.pasm=%.bin}

firmware :: ${pasm_binaries}

%.bin: %.pasm
	pasm -V3 -b $<

.DELETE_ON_ERROR:
