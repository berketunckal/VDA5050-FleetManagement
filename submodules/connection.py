import json
import os
import jsonschema
from jsonschema import validate
import logging

class ConnectionHandler:
    def __init__(self, fleetname, version, versions):
        self.fleetname = fleetname
        self.version = version
        self.versions = versions

        self.logger = logging.getLogger('ConnectionHandler')
        logging.basicConfig(level=logging.INFO)

        schema_path = os.path.join(os.path.dirname(__file__), 'schemas', 'connection.schema')
        with open(schema_path, 'r') as schema_file:
            self.connection_schema = json.load(schema_file)

    def validate_message(self, message):
        """Gelen JSON mesajını verilen şemaya göre doğrular."""
        try:
            validate(instance=message, schema=self.connection_schema)
            self.logger.info("Message is valid according to the schema.")
        except jsonschema.exceptions.ValidationError as e:
            self.logger.error(f"Schema validation failed: {e.message}")
            raise

    def process_connection_message(self, message):
        """Bağlantı mesajını işler."""
        connection_state = message.get("connectionState", "UNKNOWN")
        agv_id = message.get("serialNumber", "UNKNOWN")
        self.logger.info(f"AGV {agv_id} is now {connection_state}")

    def subscribe_to_topics(self, mqtt_client):
        """MQTT istemcisi ile abone olunacak topic'leri tanımlar."""
        topic = f"{self.fleetname}/{self.versions}/+/+/connection"
        mqtt_client.subscribe(topic, qos=1)
        self.logger.info(f"Subscribed to topic: {topic}")
