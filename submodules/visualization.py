import json
import logging
import os
from jsonschema import validate, ValidationError

class VisualizationSubscriber:
    def __init__(self, fleetname, version, versions, manufacturer):
        self.fleetname = fleetname
        self.version = version
        self.versions = versions
        self.manufacturer = manufacturer

        self.logger = logging.getLogger('VisualizationSubscriber')
        logging.basicConfig(level=logging.WARN)

        schema_path = os.path.join(os.path.dirname(__file__), 'schemas', 'visualization.schema')
        with open(schema_path, 'r') as schema_file:
            self.visualization_schema = json.load(schema_file)

    def subscribe_to_topics(self, mqtt_client):
        topic = f"{self.fleetname}/{self.versions}/{self.manufacturer}/+/visualization"
        mqtt_client.subscribe(topic, qos=0)
        self.logger.info(f"Subscribed to visualization topic: {topic}")

    def validate_message(self, message):
        try:
            validate(instance=message, schema=self.visualization_schema)
        except ValidationError as e:
            self.logger.error(f"Schema validation failed: {e.message}")
            raise

    def process_visualization_message(self, message):
        self.validate_message(message)
        agv_position = message.get("agvPosition", {})
        velocity = message.get("velocity", {})
        
        self.logger.info(f"AGV Position: x={agv_position.get('x')}, y={agv_position.get('y')}, theta={agv_position.get('theta')}")
        self.logger.info(f"AGV Velocity: vx={velocity.get('vx')}, vy={velocity.get('vy')}, omega={velocity.get('omega')}")

        self.logger.info("Visualization message processed successfully.")
