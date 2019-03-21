all:
	x86_64-linux-gnu-gcc -shared -fPIC -O2 -I/usr/include/python2.7 -L/usr/lib/x86_64-linux-gnu ValueLag.c -o ValueLag.so -lpython2.7
	x86_64-linux-gnu-gcc -shared -fPIC -O2 -I/usr/include/python2.7 -L/usr/lib/x86_64-linux-gnu Crossover.c -o Crossover.so -lpython2.7
	x86_64-linux-gnu-gcc -shared -fPIC -O2 -I/usr/include/python2.7 -L/usr/lib/x86_64-linux-gnu FastMinMax.c -o FastMinMax.so -lpython2.7
	x86_64-linux-gnu-gcc -shared -fPIC -O2 -I/usr/include/python2.7 -L/usr/lib/x86_64-linux-gnu PriceSegmentNode.c -o PriceSegmentNode.so -lpython2.7
	x86_64-linux-gnu-gcc -shared -fPIC -O2 -I/usr/include/python2.7 -L/usr/lib/x86_64-linux-gnu Kline.c -o Kline.so -lpython2.7
	x86_64-linux-gnu-gcc -shared -fPIC -O2 -I/usr/include/python2.7 -L/usr/lib/x86_64-linux-gnu PriceSpread.c -o PriceSpread.so -lpython2.7

clean:
	rm -f *.so
