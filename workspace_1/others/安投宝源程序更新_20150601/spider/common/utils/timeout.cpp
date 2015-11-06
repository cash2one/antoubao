#include <stdlib.h>
#include "timeout.h"

timeout_node_t *timeout_t::pop(void)
{
    timeout_node_t *node = NULL;
    if (head && head->etime <= nowtime) {
        node = head;
        head = head->next;
        if (head) {
            head->prev = NULL;
        }
        node->prev = NULL;
        node->next = NULL;
        if (node == tail) {
            tail = NULL;
        }
    }
    return node;
}

timeout_node_t *timeout_t::push(timeout_node_t *node)
{
    node->etime = nowtime + timeout;
    node->prev = tail;
    node->next = NULL;
    if (tail) {
        tail->next = node;
    }
    tail = node;
    if (!head) {
        head = node;
    }
    return node;
}

timeout_node_t *timeout_t::extract(timeout_node_t *node)
{
    if (node->prev) {
        node->prev->next = node->next;
    }
    if (node->next) {
        node->next->prev = node->prev;
    }
    if (node == head) {
        head = node->next;
    }
    if (node == tail) {
        tail = node->prev;
    }
    node->prev = NULL;
    node->next = NULL;
    return node;
}

timeout_node_t *timeout_t::createnode(void *p, int mark)
{
    timeout_node_t *node = (timeout_node_t *)malloc(sizeof(timeout_node_t));
    if (node) {
        node->p = p;
        node->mark = mark;
        push(node);
    }
    return node;
}

timeout_node_t *timeout_t::update(timeout_node_t *node)
{
    extract(node);
    push(node);
    return node;
}

void timeout_t::clear(void)
{
    timeout_node_t *p = head;
    while (p) {
        timeout_node_t *t = p;
        p = p->next;
        free(t);
    }
    head = NULL;
    tail = NULL;
}

