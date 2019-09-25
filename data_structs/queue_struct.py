from data_structs.doubly_linked_list import DoublyLinkedList

class Queue:
  def __init__(self):
    self.storage = DoublyLinkedList()

  def push(self, value):
    # store to head
    return self.storage.add_to_head(value)
  
  def pop(self):
    # remove from tail
    return self.storage.remove_from_tail()

  def __len__(self):
    # call len
    return len(self.storage)
