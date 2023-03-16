import javax.jms.Connection;
import javax.jms.ConnectionFactory;
import javax.jms.Destination;
import javax.jms.Message;
import javax.jms.MessageConsumer;
import javax.jms.MessageProducer;
import javax.jms.Session;
import javax.jms.TextMessage;
import org.apache.activemq.ActiveMQConnectionFactory;

public class AMQFailoverTest {

    private static final String BROKER_URL = "failover:(tcp://master-broker-url:61616,tcp://slave-broker-url:61616)";
    private static final String QUEUE_NAME = "test.queue";
    private static final int MESSAGE_COUNT = 10;

    public static void main(String[] args) throws Exception {

        // Create a connection factory
        ConnectionFactory connectionFactory = new ActiveMQConnectionFactory(BROKER_URL);

        // Create a connection
        Connection connection = connectionFactory.createConnection();

        // Start the connection
        connection.start();

        // Create a session
        Session session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);

        // Create a destination (queue)
        Destination destination = session.createQueue(QUEUE_NAME);

        // Create a message producer
        MessageProducer producer = session.createProducer(destination);

        // Send some test messages
        for (int i = 0; i < MESSAGE_COUNT; i++) {
            String messageText = "Test message " + (i + 1);
            TextMessage message = session.createTextMessage(messageText);
            producer.send(message);
            System.out.println("Sent message: " + messageText);
        }

        // Create a message consumer
        MessageConsumer consumer = session.createConsumer(destination);

        // Receive and process messages
        for (int i = 0; i < MESSAGE_COUNT; i++) {
            Message message = consumer.receive();
            String messageText = ((TextMessage) message).getText();
            System.out.println("Received message: " + messageText);
        }

        // Close the session and connection
        session.close();
        connection.close();
    }
}
