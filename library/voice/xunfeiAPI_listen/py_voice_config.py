import os
import sys
import shutil
import subprocess as sp
from time import sleep

def cp_libs(file_path):
    lib_path = os.path.join(file_path,"lib/libmsc.so")
    print "lib_path: ", lib_path
    os.system("cp " + lib_path + " ./lib/")
    msc_path = os.path.join(file_path,"bin/msc/")
    os.system("cp -r "+ msc_path +  " ./build/bin")

def cp_msc(file_path):

    msc_path = os.path.join(file_path,"bin/msc/")
    print "msc_path: ", msc_path
    os.system("cp -r "+ msc_path +  " ./build/bin")


def cp_bin_folder():
    try:
        os.mkdir("build")
    except:
        print "dir exists"
    # shutil.copytree("bin/","build/")
    os.system("cp -r ./bin/ ./build/")


def use_cmake():
    build_path = os.path.join(os.path.realpath(os.getcwd()), "build")
    print "build path: ", build_path
    sp.call("cmake ../",shell = True, cwd =build_path)

    sleep(1)
    sp.call("make",shell = True, cwd =build_path)


def main():

    if len(sys.argv) != 2:
        print "usage: python py_voice_config.py <path_to_xunfei>"
        sys.exit(1)
    else:
        xf_path = sys.argv[1]
        
    cp_libs(xf_path)
    cp_bin_folder()
    cp_msc(xf_path)
    use_cmake()


if __name__ == '__main__':
    main()
