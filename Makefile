CC := gcc -Wall -ggdb3 -fPIC

run-demo: demo libc-intercept 
	@echo
	@echo '$$ LD_PRELOAD=./libc-intercept.so ./demo'
	@LD_PRELOAD=./libc-intercept.so ./demo

libc-intercept: tlv-client.o libc-intercept.c
	$(CC) -shared -o libc-intercept.so tlv-client.o libc-intercept.c -ldl

demo: demo.c
	gcc -ggdb3 -o demo demo.c -pthread

clean:
	rm -f demo tlv-client.o libc-intercept.so

.PHONY: all clean run-demo
