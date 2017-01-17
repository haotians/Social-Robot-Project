#!/bin/sh
makedir( ){
	file_mode=$1
	shift
	dir_name="$1"
	if [ $file_mode -eq '1' ]; then
		dir_name=`dirname $1`
	fi
	if [ ! -d "$dir_name" ]; then
		echo "Create $dir_name"
	fi
	mkdir -p $dir_name
}

fmode=0
if [ "-f" = "$1" ]; then
	fmode=1
	shift
fi
for i in $@; do
	makedir $fmode $i
done
