import sys
from doubly_linked_list import DoublyLinkedList

class Queue:
  def __init__(self):
    self.storage = DoublyLinkedList()

  def enqueue(self, value):
    # store to head
    return self.storage.add_to_head(value)
  
  def dequeue(self):
    # remove from tail
    return self.storage.remove_from_tail()

  def len(self):
    # call len
    return self.storage.__len__()
