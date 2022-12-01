#include <arpa/inet.h>
#include <asm-generic/socket.h>
#include <dlfcn.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/un.h>
#include <unistd.h>

#include "tlv-client.h"

#define DIVIDE_ROUND_UP(val, div) (val + (div - 1)) / div

#define SOCK_PATH "/tmp/socket_test.s"

static int __socketfd = -1;

#define TLV_LEN 16
#define TLV_PREFIX_LEN (sizeof(enum tlv_tag) + sizeof(int))
#define TLV_MESSAGE_LEN TLV_LEN - TLV_PREFIX_LEN

struct tlv_message {
  enum tlv_tag tag;
  int length;
  char value[TLV_MESSAGE_LEN];
};

void close_socket_if_open() {
  if (__socketfd != -1) {
    close(__socketfd);
    __socketfd = -1;
  }
}

static int get_socket() {
  if (__socketfd != -1) {
    return __socketfd;
  }

  // Create a socket
  __socketfd = socket(AF_UNIX, SOCK_STREAM, 0);
  if (__socketfd == -1) {
    perror("socket() failed");
    goto err;
  }

  const int enable = 1;
  if (setsockopt(__socketfd, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int)) <
      0) {
    perror("setsockopt(SO_REUSEADDR) failed");
  }
  if (setsockopt(__socketfd, SOL_SOCKET, SO_REUSEPORT, &enable, sizeof(int)) <
      0) {
    perror("setsockopt(SO_REUSEPORT) failed");
  }

  // Get the server address in order
  struct sockaddr_un serveraddr;
  memset(&serveraddr, 0, sizeof(serveraddr));
  serveraddr.sun_family = AF_UNIX;
  strcpy(serveraddr.sun_path, SOCK_PATH);

  // Connect to the server
  int res =
      connect(__socketfd, (struct sockaddr *)&serveraddr, SUN_LEN(&serveraddr));
  if (res < 0) {
    perror("connect() failed");
    goto err;
  }

  return __socketfd;

err:
  // Close socket (connection wouldn't have gone through, not need to check)
  close_socket_if_open();

  return -1;
}

int send_message(enum tlv_tag tag, int length, void *value) {
  int sock = get_socket();
  if (sock == -1) {
    return -1;
  }

  struct tlv_message msg;
  msg.tag = htonl(tag);

  printf("%d %ld %ld\n", TLV_LEN, TLV_PREFIX_LEN, TLV_MESSAGE_LEN);

  for (int i = 0; i < length; i += TLV_MESSAGE_LEN) {
    msg.length = htonl(length);

    int msglen =
        (length - i) > TLV_MESSAGE_LEN ? TLV_MESSAGE_LEN : (length - i);
    memset(msg.value, 0, TLV_MESSAGE_LEN);
    memcpy(msg.value, value + i, msglen);

    write(STDOUT_FILENO, "Sending '", 9);
    write(STDOUT_FILENO, &msg.value, msglen);
    write(STDOUT_FILENO, "'\n", 2);

    int rc = send(sock, &msg, sizeof(msg), 0);
    if (rc != 0) {
      perror("send() failed for tlv message\n");
    }
  }

  close_socket_if_open();

  return -1;
}
