#include <pthread.h>
#include <stdio.h>

pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

int main(int argc, char *argv[]) {
  printf("Creating mutex\n");

  pthread_mutex_lock(&mutex);
  pthread_mutex_unlock(&mutex);

  printf("Hello world\n");
}
