#define _GNU_SOURCE

#include <dlfcn.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/un.h>
#include <unistd.h>

#include "tlv-client.h"

static int (*o_pthread_mutex_lock)(pthread_mutex_t *) = NULL;
static int (*o_pthread_mutex_unlock)(pthread_mutex_t *) = NULL;

int pthread_mutex_lock(pthread_mutex_t *mutex) {
  pthread_t tid = pthread_self();
  printf("Locking mutex from TID %lu\n", tid);

  if (o_pthread_mutex_lock == NULL) {
    o_pthread_mutex_lock = dlsym(RTLD_NEXT, "pthread_mutex_lock");
  }

  char msg[] = "Locked!";
  send_message(MUTEX_LOCK, sizeof(msg), msg);

  return (*o_pthread_mutex_lock)(mutex);
}

int pthread_mutex_unlock(pthread_mutex_t *mutex) {
  pthread_t tid = pthread_self();
  printf("Unlocking mutex from TID %lu\n", tid);

  if (o_pthread_mutex_unlock == NULL) {
    o_pthread_mutex_unlock = dlsym(RTLD_NEXT, "pthread_mutex_unlock");
  }

  char msg[] = "Unlocked!";
  send_message(MUTEX_UNLOCK, sizeof(msg), msg);

  return (*o_pthread_mutex_unlock)(mutex);
}
