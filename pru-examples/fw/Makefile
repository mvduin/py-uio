pasm_sources := $(wildcard *.pasm)
pasm_binaries := ${pasm_sources:%.pasm=%.bin}

PASM = pasm
PASMFLAGS = -V3
PASMFLAGS += -L   # generate annotated source listing
PASMFLAGS += -d   # generate debug data

SHELL := bash

firmware :: ${pasm_binaries}

clean ::
	${RM} ${pasm_binaries} ${pasm_sources:%.pasm=%.txt} *.dbg

${pasm_binaries}: %: $(wildcard *.h)

# reduce the amount of spam produced by pasm

%.bin: %.pasm
	@echo ${PASM} ${PASMFLAGS} -b $<
	@set -o pipefail; ${PASM} ${PASMFLAGS} -b $< | { grep -P '\b: '; true; }

.DELETE_ON_ERROR:
