import sys
import time
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container

class Producer(MessagingHandler):
    def __init__(self, urls, address, num_messages, delay):
        super(Producer, self).__init__()
        self.urls = urls
        self.address = address
        self.num_messages = num_messages
        self.delay = delay
        self.sent_messages = 0

    def connect_to_broker(self, event):
        for url in self.urls:
            try:
                conn = event.container.connect(url, reconnect=False)
                sender = event.container.create_sender(conn, self.address)
                self.connected_broker = url
                print(f"Producer connected to broker: {url}")
                return sender
            except Exception as e:
                print(f"Failed to connect to broker at {url}: {e}")
        else:
            print("All brokers are down, exiting")
            event.container.stop()
            return None

    def on_start(self, event):
        self.sender = self.connect_to_broker(event)

def on_sendable(self, event):
    while self.sent_messages < self.num_messages:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            msg_body = f"Hello World! Message {self.sent_messages + 1} at {current_time}"
            msg = Message(body=msg_body)
            event.sender.send(msg)
            print(f"Message sent to broker {self.connected_broker}: {msg.body}")
            self.sent_messages += 1
            time.sleep(self.delay)
        except Exception as e:
            print(f"Failed to send message: {e}")
            self.sender.close()
            self.sender = self.connect_to_broker(event)

            if self.sender is None:
                break
    else:
        event.sender.close()


# ...

if __name__ == "__main__":
    broker_urls = ["amqp://localhost:5672", "amqp://localhost:5673"]
    address = "test_queue"
    num_messages = 100
    delay = 0.5

    # Start the consumer
    consumer = Consumer(broker_urls, address)
    Container(consumer).run()

    time.sleep(2)

    # Start the producer
    producer = Producer(broker_urls, address, num_messages, delay)
    Container(producer).run()
