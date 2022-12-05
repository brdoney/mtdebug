#define _GNU_SOURCE

#include <dlfcn.h>
#include <jansson.h>
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

#define MAX_MESSAGE_LEN 32

static char *json_message(pthread_t tid, pthread_mutex_t *mutex) {
  char address[MAX_MESSAGE_LEN];
  snprintf(address, MAX_MESSAGE_LEN, "%p", mutex);

  json_t *json = json_object();
  json_object_set_new(json, "address", json_string(address));
  json_object_set_new(json, "thread", json_integer(tid));
  char *res = json_dumps(json, 0);

  json_decref(json);

  return res;
}

int pthread_mutex_lock(pthread_mutex_t *mutex) {
  pthread_t tid = pthread_self();
  printf("Locking mutex from TID %lu\n", tid);

  if (o_pthread_mutex_lock == NULL) {
    o_pthread_mutex_lock = dlsym(RTLD_NEXT, "pthread_mutex_lock");
  }

  char *msg = json_message(tid, mutex);
  send_message(MUTEX_LOCK, strlen(msg), msg);
  free(msg);

  // Run the actual mutex lock (which might block while waiting)
  int res = (*o_pthread_mutex_lock)(mutex);
  if (res != 0) {
    return res;
  }

  // Notify that we've claimed the mutex
  msg = json_message(tid, mutex);
  send_message(MUTEX_CLAIM, strlen(msg), msg);
  free(msg);

  return res;
}

int pthread_mutex_unlock(pthread_mutex_t *mutex) {
  pthread_t tid = pthread_self();
  printf("Unlocking mutex from TID %lu\n", tid);

  if (o_pthread_mutex_unlock == NULL) {
    o_pthread_mutex_unlock = dlsym(RTLD_NEXT, "pthread_mutex_unlock");
  }

  char *msg = json_message(tid, mutex);
  send_message(MUTEX_UNLOCK, strlen(msg), msg);
  free(msg);

  return (*o_pthread_mutex_unlock)(mutex);
}
