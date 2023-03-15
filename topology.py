import argparse
import qpid_proton as proton

def fetch_topology(url, address):
    conn = proton.Connection(url)
    conn.container.container_id = "fetch_topology"
    conn.open()

    receiver = conn.create_receiver(None, dynamic=True)
    sender = conn.create_sender(address)

    request = proton.Message()
    request.properties = {
        "operation": "QUERY",
        "entityType": "org.apache.qpid.dispatch.router"
    }
    request.reply_to = receiver.remote_source.address
    sender.send(request)

    while not conn.closed:
        try:
            event = conn.container.next_event()
            if event.type == proton.Event.MESSAGE and event.link == receiver:
                print("Cluster topology:")
                for node in event.message.body['results']:
                    print(f"Node: {node[0]}, Router ID: {node[1]}")
                conn.close()
        except KeyboardInterrupt:
            conn.close()
            break
            
    broker_address = sender.connection.transport._transport.get_connection().get_peer_address()
    broker_address = sender.connection.transport.get_connection().get_remote_address()


    # Send a message to the queue
    message = Message(content="Hello, world!")
    sender.send(message)

    # Print the broker address
    print("Active broker:", broker_address)
    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AMQ Cluster Topology Fetcher")
    parser.add_argument("-u", "--url", required=True, help="AMQ broker URL")
    parser.add_argument("-a", "--address", default="$management", help="Management address (default: $management)")

    args = parser.parse_args()

    fetch_topology(args.url, args.address)
