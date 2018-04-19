pasm_sources := $(wildcard *.pasm)
pasm_binaries := ${pasm_sources:%.pasm=%.bin}

SHELL := bash

firmware :: ${pasm_binaries}

%.bin: %.pasm
	@echo pasm -V3 -b $<
	@set -o pipefail; pasm -V3 -b $< | { grep -P '\b: '; true; }

.DELETE_ON_ERROR:
