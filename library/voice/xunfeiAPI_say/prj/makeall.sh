#! /bin/bash
export BASEDIR=$PWD

MODULE_TARGET=(			\
	ivwdemo				\
	)

for target in ${MODULE_TARGET[*]}
do
    cd $BASEDIR/../examples/$target
    make
done

