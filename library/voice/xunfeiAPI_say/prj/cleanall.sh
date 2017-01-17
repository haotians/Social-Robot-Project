#! /bin/bash
export BASEDIR=$PWD

MODULE_TARGET=(			\
	ivwdemo				\
	)

for target in ${MODULE_TARGET[*]}
do
    if test -d $BASEDIR/../examples/$target/xebug
        then rm -r $BASEDIR/../examples/$target/xebug
	echo delete $BASEDIR/../examples/$target/xebug
    fi

    if test -d $BASEDIR/../examples/$target/xelease
        then rm -r $BASEDIR/../examples/$target/xelease
	echo delete $BASEDIR/../examples/$target/xelease
    fi

    if test -f ../bin/$target
        then rm ../bin/$target
	echo delete ../bin/$target
    fi
done
echo clean done!
