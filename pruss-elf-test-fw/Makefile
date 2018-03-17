# disable all built-in rules; TI toolchain uses totally incompatible syntax
MAKEFLAGS += -r -R

RM = rm -f

cgt_root := $(patsubst %/bin/clpru,%,$(realpath $(shell which clpru)))

CL = clpru
CL += -I${cgt_root}/include -i${cgt_root}/lib
# target options
CL += -v3
CL += --hardware_mac=on
# language options
CL += --gcc
# codegen options
CL += -O2 -mf
#CL += -op0	# assume functions may be called from elsewhere
#CL += --symdebug:none	# annoying when reading .asm
# output options
#CL += -k	# keep intermediate .asm
# linker options
#LDFLAGS += --make_static
LDFLAGS += --output_file=$@
#LDFLAGS += --map_file=$@.map
#LDFLAGS += --xml_link_info=$@.xml

all :: test.out

clean ::
	${RM} test.out

test.out: test.obj
	${CL} $^ -z ${LDFLAGS} am335x.cmd


%.obj: %.c
	${CL} $<

clean ::
	${RM} *.out *.obj *.out.map *.out.xml *.asm
