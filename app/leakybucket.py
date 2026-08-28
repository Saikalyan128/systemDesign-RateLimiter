import time
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

class Queue:
  def __init__(self):
    self.queue = []
    
  def enqueue(self, element):
    self.queue.append(element)

  def dequeue(self):
    if self.isEmpty():
      raise IndexError("dequeue from an empty queue")
    return self.queue.pop(0)

  def peek(self):
    if self.isEmpty():
      raise IndexError("peek from an empty queue")
    return self.queue[0]

  def isEmpty(self):
    return len(self.queue) == 0

  def size(self):
    return len(self.queue)

class LeakyBucketAlgo(object):

    def __init__(self, queue_size=5, outflow_rate=2):
        logger.info("Initiating Leaky bucket technique")

        # Initiate parameters
        self.queue_size = queue_size
        self.outflow_rate = outflow_rate
        self.start_time = time.time()
        self.queue = Queue()

    def refill(self):

        now = time.time()
        elapsed_time = now - self.start_time
        outflow = int(elapsed_time * self.outflow_rate)
        for _ in range(0, outflow):
           if self.queue.isEmpty():
              break
           self.queue.dequeue()
        if outflow > 0:
           self.start_time += outflow / self.outflow_rate
        logger.info(f"current tokens in queue : {self.queue.size()}")
        return self.queue.size()


    def accept_request(self, tokens=1):
        """Return True and enqueue the request if there is room, else False."""
        current = self.refill()
        if current >= self.queue_size:
           return False
        self.queue.enqueue(tokens)
        return True
        
            
