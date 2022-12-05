#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

static void *thread_func(void *arg) {
  int *data = arg;
  printf("Thread starting with %d\n", *data);

  printf("Thread creating variable\n");
  int b = *data;

  pthread_mutex_lock(&mutex);
  printf("Hello from thread!\n");
  pthread_mutex_unlock(&mutex);

  printf("Thread exiting\n");

  return NULL;
}

int main(int argc, char *argv[]) {
  printf("Main starting\n");

  printf("Main creating variable\n");
  int a = 1;

  printf("Main creating thread args\n");
  int *data1 = malloc(sizeof(int));
  *data1 = -1;
  int *data2 = malloc(sizeof(int));
  *data2 = 2;

  pthread_mutex_lock(&mutex);

  printf("Main creating thread 1\n");
  pthread_t thread1;
  pthread_create(&thread1, NULL, thread_func, data1);

  printf("Main creating thread 2\n");
  pthread_t thread2;
  pthread_create(&thread2, NULL, thread_func, data2);

  pthread_mutex_unlock(&mutex);

  pthread_join(thread1, NULL);
  pthread_join(thread2, NULL);
  free(data1);
  free(data2);

  printf("Main exiting\n");
}
