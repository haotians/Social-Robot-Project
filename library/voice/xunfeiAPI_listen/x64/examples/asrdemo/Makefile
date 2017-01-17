#common makefile header

export BASEDIR=$(PWD)/../../prj
include $(BASEDIR)/scripts/configure.mk

MODULE_EXEC	= asrdemo
MODULE_TARGET	= $(MODULE_EXEC)
LOCAL_INCLUDE	= -I$(BASEDIR)/../include
LOCAL_FLAGS	= $(LOCAL_INCLUDE) $(PIC_FLAG)
LIBS	:= -L$(BASEDIR-LIB) -lmsc -ldl -lpthread -lm -lrt

MODULE_OBJ   = \
	$(MODULE_OUTPUT)/asrdemo.o

#common makefile foot
include $(BASEDIR)/scripts/rules.mk
