1. 进入文件夹
2. 将lib文件夹内的libmsc.so替换成x64内的，并且替换相应的科大讯飞id
3. `cd examples/ttsdemo`
4. `make`，编译成功
5. 运行时设置环境变量
`export LD_LIBRARY_PATH=libmsc.so所在目录:LD_LIBRARY_PATH`
6. 可运行bin下编写好的py程序或直接运行`./ttsdemo "string"`
