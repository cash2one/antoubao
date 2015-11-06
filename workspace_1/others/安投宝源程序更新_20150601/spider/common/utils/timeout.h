#ifndef _ATB_TIMEOUT_H
#define _ATB_TIMEOUT_H

#include <stdio.h>
#include <stdlib.h>

typedef struct _timeout_node_t {
    struct _timeout_node_t *prev;
    struct _timeout_node_t *next;
    void *p;
    long long etime;
    int mark;
} timeout_node_t;

typedef struct _timeout_t {
    timeout_node_t *head;
    timeout_node_t *tail;
    long long timeout;
    long long nowtime;
    void init(long long now, long long t) {nowtime = now; timeout = t; head = NULL; tail = NULL;}
    _timeout_t() {init(0, 0);}
    _timeout_t(long long t) {init(0, t);}
    _timeout_t(long long now, long long t) {init(now, t);}
    timeout_node_t *pop(void);
    timeout_node_t *push(timeout_node_t *node);
    timeout_node_t *extract(timeout_node_t *node);
    timeout_node_t *createnode(void *p, int mark = 0);
    timeout_node_t *update(timeout_node_t *node);
    void deletenode(timeout_node_t *node) {free(node);}
    void removenode(timeout_node_t *node) {extract(node); deletenode(node);}
    void refreshtime(long long t) {nowtime = t;}
    void clear(void);
} timeout_t;

#endif

