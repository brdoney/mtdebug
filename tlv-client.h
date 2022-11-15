#ifndef __TLV_CLIENT
#define __TLV_CLIENT

enum tlv_tag { MUTEX_LOCK, MUTEX_UNLOCK };

int send_message(enum tlv_tag tag, int length, void *value);

#endif
