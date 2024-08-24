import json
import os
import jsonschema
from jsonschema import validate
import logging

class FactsheetHandler:
    def __init__(self, fleetname, version, versions):
        self.fleetname = fleetname
        self.version = version
        self.versions = versions

        self.logger = logging.getLogger('FactsheetHandler')
        logging.basicConfig(level=logging.INFO)

        schema_path = os.path.join(os.path.dirname(__file__), 'schemas', 'factsheet.schema')
        with open(schema_path, 'r',  encoding="utf-8") as schema_file:
            self.factsheet_schema = json.load(schema_file)

    def validate_message(self, message):
        """Gelen JSON mesajını verilen şemaya göre doğrular."""
        try:
            validate(instance=message, schema=self.factsheet_schema)
            self.logger.info("Factsheet message is valid according to the schema.")
        except jsonschema.exceptions.ValidationError as e:
            self.logger.error(f"Factsheet schema validation failed: {e.message}")
            raise

    def process_factsheet_message(self, message):
        """Factsheet mesajını işler."""
        manufacturer = message.get("manufacturer", "UNKNOWN")
        serial_number = message.get("serialNumber", "UNKNOWN")
        self.logger.info(f"Received factsheet from {manufacturer} with Serial Number: {serial_number}")


    def subscribe_to_topics(self, mqtt_client):
        """MQTT istemcisi ile abone olunacak topic'leri tanımlar."""
        topic = f"{self.fleetname}/{self.versions}/+/+/factsheet"
        
        mqtt_client.subscribe(topic, qos=1)
        self.logger.info(f"Subscribed to topic: {topic}")
