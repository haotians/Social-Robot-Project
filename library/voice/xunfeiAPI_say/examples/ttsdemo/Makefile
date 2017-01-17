#common makefile header

export BASEDIR=$(PWD)/../../prj
include $(BASEDIR)/scripts/configure.mk

MODULE_EXEC	= ttsdemo
MODULE_TARGET	= $(MODULE_EXEC)
LOCAL_INCLUDE	= -I$(BASEDIR)/../include
LOCAL_FLAGS	= $(LOCAL_INCLUDE) $(PIC_FLAG)
LIBS	:= -L$(BASEDIR-LIB) -lmsc -ldl -lpthread -lrt -lm

MODULE_OBJ   = \
	$(MODULE_OUTPUT)/ttsdemo.o

#common makefile foot
include $(BASEDIR)/scripts/rules.mk
