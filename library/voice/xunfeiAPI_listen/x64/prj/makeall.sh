#! /bin/bash
export BASEDIR=$PWD

MODULE_TARGET=(			\
	asrdemo				\
	)

for target in ${MODULE_TARGET[*]}
do
    cd $BASEDIR/../examples/$target
    make
done

