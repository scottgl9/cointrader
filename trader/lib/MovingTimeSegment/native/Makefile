all:
	x86_64-linux-gnu-gcc -shared -fPIC -O2 -I/usr/include/python2.7 -L/usr/lib/x86_64-linux-gnu MovingTimeSegment.c -o MovingTimeSegment.so -lpython2.7
	x86_64-linux-gnu-gcc -shared -fPIC -O2 -I/usr/include/python2.7 -L/usr/lib/x86_64-linux-gnu MTSCircularArray.c -o MTSCircularArray.so -lpython2.7

clean:
	rm -f *.so
