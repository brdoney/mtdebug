#include <pthread.h>
#include <stdio.h>

static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

static void *thread_func(void *arg) {
  printf("Thread starting\n");

  pthread_mutex_lock(&mutex);
  printf("Hello from thread!\n");
  pthread_mutex_unlock(&mutex);

  printf("Thread exiting\n");

  return NULL;
}

int main(int argc, char *argv[]) {
  printf("Main starting\n");

  pthread_mutex_lock(&mutex);

  printf("Main creating thread\n");
  pthread_t thread;
  pthread_create(&thread, NULL, thread_func, NULL);

  pthread_mutex_unlock(&mutex);

  pthread_join(thread, NULL);

  printf("Main exiting\n");
}
