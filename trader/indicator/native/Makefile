all:
	x86_64-linux-gnu-gcc -shared -fPIC -O2 -I/usr/include/python2.7 -L/usr/lib/x86_64-linux-gnu SMA.c -o SMA.so -lpython2.7
	x86_64-linux-gnu-gcc -shared -fPIC -O2 -I/usr/include/python2.7 -L/usr/lib/x86_64-linux-gnu EMA.c -o EMA.so -lpython2.7
	x86_64-linux-gnu-gcc -shared -fPIC -O2 -I/usr/include/python2.7 -L/usr/lib/x86_64-linux-gnu AEMA.c -o AEMA.so -lpython2.7

clean:
	rm -f *.so
