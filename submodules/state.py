import json
import os
import logging
from jsonschema import validate, ValidationError

class StateHandler:
    def __init__(self, fleetname, version, versions):
        self.fleetname = fleetname
        self.version = version
        self.versions = versions

        self.logger = logging.getLogger('StateHandler')
        logging.basicConfig(level=logging.INFO)

        schema_path = os.path.join(os.path.dirname(__file__), 'schemas', 'state.schema')
        with open(schema_path, 'r',  encoding="utf-8") as schema_file:
            self.state_schema = json.load(schema_file)

    def subscribe_to_topics(self, mqtt_client):
        """State mesajlarına abone olur."""
        topic = f"{self.fleetname}/{self.versions}/+/+/state"
        mqtt_client.subscribe(topic, qos=1)
        self.logger.info(f"Subscribed to state topic: {topic}")

    def validate_message(self, message):
        """Gelen JSON mesajını şemaya göre doğrular."""
        try:
            validate(instance=message, schema=self.state_schema)
            self.logger.info("State message is valid according to the schema.")
        except ValidationError as e:
            self.logger.error(f"State schema validation failed: {e.message}")
            raise

    def process_state_message(self, message):
        """State mesajını işler."""
        order_id = message.get("orderId")
        driving_status = message.get("driving")
        battery_state = message.get("batteryState", {}).get("batteryCharge")

        self.logger.info(f"Processing state for Order ID: {order_id}")
        self.logger.info(f" - Driving: {driving_status}")
        self.logger.info(f" - Battery Charge: {battery_state}%")
