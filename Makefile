CC := gcc -Wall -ggdb3

run-demo: demo libc-intercept 
	@echo
	@echo '$$ LD_PRELOAD=./libc-intercept.so ./demo'
	@LD_PRELOAD=./libc-intercept.so ./demo

libc-intercept: libc-intercept.c
	$(CC) -fPIC -shared -o libc-intercept.so libc-intercept.c -ldl

demo: demo.c
	$(CC) -o demo demo.c -pthread

clean:
	rm demo

.PHONY: all clean run-demo
