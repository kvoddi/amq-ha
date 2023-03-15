import sys
import argparse
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container
from proton.utils import BlockingConnection
from proton import symbol

class TopologyFetcher(MessagingHandler):
    def __init__(self, url, address):
        super(TopologyFetcher, self).__init__()
        self.url = url
        self.address = address

    def on_start(self, event):
        self.container = event.container
        self.connection = event.container.connect(self.url, reconnect=False)
        self.receiver = event.container.create_receiver(self.connection, None, dynamic=True)
        self.sender = event.container.create_sender(self.connection, self.address)

    def on_link_opened(self, event):
        if event.receiver == self.receiver:
            request = Message()
            request.properties = {symbol("operation"): symbol("QUERY"),
                                  symbol("entityType"): symbol("org.apache.qpid.dispatch.router")}
            request.reply_to = self.receiver.remote_source.address
            self.sender.send(request)

    def on_message(self, event):
        print("Cluster topology:")
        for node in event.message.body['results']:
            print(f"Node: {node[0]}, Router ID: {node[1]}")

        event.connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AMQ Cluster Topology Fetcher")
    parser.add_argument("-u", "--url", required=True, help="AMQ broker URL")
    parser.add_argument("-a", "--address", default="$management", help="Management address (default: $management)")

    args = parser.parse_args()

    topology_fetcher = TopologyFetcher(args.url, args.address)
    Container(topology_fetcher).run()
