all:
	x86_64-linux-gnu-gcc -shared -fPIC -O2 -I/usr/include/python2.7 -L/usr/lib/x86_64-linux-gnu ValueLag.c -o ValueLag.so -lpython2.7
	x86_64-linux-gnu-gcc -shared -fPIC -O2 -I/usr/include/python2.7 -L/usr/lib/x86_64-linux-gnu Crossover.c -o Crossover.so -lpython2.7
	x86_64-linux-gnu-gcc -shared -fPIC -O2 -I/usr/include/python2.7 -L/usr/lib/x86_64-linux-gnu FastMinMax.c -o FastMinMax.so -lpython2.7
	x86_64-linux-gnu-gcc -shared -fPIC -O2 -I/usr/include/python2.7 -L/usr/lib/x86_64-linux-gnu PriceSegmentTree.c -o PriceSegmentTree.so -lpython2.7

clean:
	rm -f *.so
