#define _GNU_SOURCE

#include <dlfcn.h>
#include <pthread.h>
#include <stdio.h>
#include <unistd.h>

// Interface with a socket that the server will open
// Intercept libc sync API calls to track things, updates will be given over the
// socket

// We can't intercept PTHREAD_MUTEX_INIT and similar macros, since they're
// defined at compile time and don't piggyback on pthread_mutex_init

static int (*o_pthread_mutex_lock)(pthread_mutex_t *) = NULL;
static int (*o_pthread_mutex_unlock)(pthread_mutex_t *) = NULL;

int pthread_mutex_lock(pthread_mutex_t *mutex) {
  pthread_t tid = pthread_self();
  printf("Locking mutex from TID %lu\n", tid);

  if (o_pthread_mutex_lock == NULL) {
    o_pthread_mutex_lock = dlsym(RTLD_NEXT, "pthread_mutex_lock");
  }

  return (*o_pthread_mutex_lock)(mutex);
}

int pthread_mutex_unlock(pthread_mutex_t *mutex) {
  pthread_t tid = pthread_self();
  printf("Unlocking mutex from TID %lu\n", tid);

  if (o_pthread_mutex_unlock == NULL) {
    o_pthread_mutex_unlock = dlsym(RTLD_NEXT, "pthread_mutex_unlock");
  }

  return (*o_pthread_mutex_unlock)(mutex);
}
