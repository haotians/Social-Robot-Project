##Package requires for robotic system:

###0.VAL/VAL4
**(importtant!!!!must install this before opencv)**

    sudo apt-get install libv4l-dev

###1.OpenCv2
  chech the link below for more info on opencv installtion 
  NOTE: our system works on opencv 2.4.10 instead of 2.4.9
	remember to make according changes in the link below
  http://my.oschina.net/u/1757926/blog/293976

###2.PyAudio

	sudo apt-get install python-pyaudio

###3.Pip
	sudo apt-get install python-pip python-dev build-essential 
	sudo pip install --upgrade pip 
	sudo pip install --upgrade virtualenv 
  

###4.PyBaiduYuyin

**Not required any more, included in the package**

	sudo pip install PyBaiduYuyin

###5.pyttsx

	sudo pip install pyttsx

###6.SpeechRecogintion

**Not required any more, included in the package**

	sudo pip install SpeechRecongnition

###7.Mpg123 

**Not required any more, included in the package**

	sudo apt-get install mpg123

###8.Flac

	sudo apt-get install flac

###9.pygame 

**Not required any more, included in the package**

	sudo apt-get install python-pygame

###10.easy_install

	sudo apt-get install python-setuptools python-dev build-essential 
	sudo easy_install pip 
    sudo pip install --upgrade virtualenv 
   

###11.pyfirmata

**Not required any more**

	sudo easy_install pyfirmata

###12.python_addin

	sudo apt-get install python-numpy python-scipy

###13._tkinter

	sudo apt-get install python-tk

###14.ffmpeg
	sudo add-apt-repository ppa:kirillshkrogalev/ffmpeg-next
	sudo apt-get update
	sudo apt-get install ffmpeg

###15.socketIO_client

	sudo pip install socketIO-client

###16.matplotlib
	sudo apt-get install python-matplotlib

###17.beautifulsoup
	sudo apt-get install python-bs4

###18.caffe
	// this is a CPU only version of caffe

	step 0
	//find Makefile.config CMakeCache.txt CaffeConfig.cmake in Vision/library/caffe_config

	step 1
	sudo apt-get install build-essential
	sudo apt-get install libprotobuf-dev libleveldb-dev libsnappy-dev libopencv-dev libboost-all-dev
	sudo apt-get install libhdf5-serial-dev libgflags-dev libgoogle-glog-dev liblmdb-dev protobuf-compiler
	sudo apt-get install libatlas-base-dev

	step 2
	cd Github(or any place you want)
	git clone https://github.com/BVLC/caffe.git
	cd caffe/python
	for req in $(cat requirements.txt); do sudo pip install $req; done
	cd ..
	mkdir build
	
	step3
	// copy Makefile.config to caffe dir
	cd build
	cmake ..

	step4
	// In CMakeCache.txt, replace CPU_ONLY:BOOL=OFF by CPU_ONLY:BOOL=ON
	// In CaffeConfig.cmake, replace set(Caffe_CPU_ONLY OFF) by set(Caffe_CPU_ONLY ON)
	make all -j4
	make test
	make runtest
	make pycaffe

	step5
	// remember to change the caffe path in the source code

###19. dlib
	go to http://dlib.net/compile.html download dlib 18.18
	unpack
	Go to the base folder of the dlib repository and run python setup.py install.

###20. ssh server and client for ssh control (ssh mini@192.168.31.129 /193)
    sudo apt-get install openssh-server
    sudo apt-get install openssh-client

###21. xunfei listen install (jingwei@ewaybot.com  password:july2015)
	# cd xx/xx/Vision/library/voice/xunfeiAPI_listen/
	# find Linux_aitalk_2.002_56a77064.zip
	# unzip, use x64 replace xx/xx/Vision/library/voice/xunfeiAPI_listen/x64
	# cd xx/xx/Vision/library/voice/xunfeiAPI_listen/src
	# open vsr.cpp, find appid ,then set appid = 56a77064
	# cd ..
	# python py_voice_config.py x64/
	# cd build/bin/
	# ./asr
	# if ok, you success

###22. xunfei speak install (jingwei@ewaybot.com  password:july2015)
	# cd xx/xx/Vision/library/voice/xunfeiAPI_say/
	# find Linux_aitalk_2.002_56a77064.zip
	# unzip, replace everything in the base directory with the folders in the zip file
	# cd xunfeiAPI_say/lib, copy libmsc.so in x64 folder to the lib directory and replace its counterpart

	# cd xunfeiAPI_say/examples/ttsdemo
	# open ttedemo.c, find appid ,then set appid = 56a77064; set const char* text  = argv[1]; comment //key = getchar();
	# make
