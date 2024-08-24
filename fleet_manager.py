import json
import os
import paho.mqtt.client as mqtt
import logging
from submodules.connection import ConnectionHandler
from submodules.factsheet import FactsheetHandler
from submodules.instant_actions import InstantActionsPublisher
from submodules.order import OrderPublisher
from submodules.state import StateHandler
from submodules.visualization import VisualizationSubscriber
import yaml
import jsonschema

class FleetManager:
    def __init__(self):
        self.logger = logging.getLogger('FleetManager')
        logging.basicConfig(level=logging.INFO)

        config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
        with open(config_path, 'r') as config_file:
            config = yaml.safe_load(config_file)

        mqtt_config = config['mqtt']
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        fleet_info = config['fleet_info']
        self.fleetname = fleet_info['fleetname']
        self.version = fleet_info['version']
        self.versions = fleet_info['versions']
        self.manufacturer = fleet_info['manufacturer']

        self.connection_handler = ConnectionHandler(self.fleetname, self.version, self.versions)
        self.factsheet_handler = FactsheetHandler(self.fleetname, self.version , self.versions)
        self.instant_actions_publisher = InstantActionsPublisher(self.fleetname, self.version, self.versions, self.manufacturer, "001")
        self.order_publisher = OrderPublisher(self.fleetname, self.version, self.versions, self.manufacturer, "001")
        self.state_handler = StateHandler(self.fleetname, self.version, self.versions)
        self.visualization_subscriber = VisualizationSubscriber(self.fleetname, self.version, self.versions, self.manufacturer)
        
        self.mqtt_client.connect(mqtt_config['broker_address'], mqtt_config['broker_port'], mqtt_config['keep_alive'])

    def on_connect(self, client, userdata, flags, rc, *extra):
        if rc == 0:
            self.logger.info("Connected to MQTT broker successfully.")
            self.connection_handler.subscribe_to_topics(self.mqtt_client)
            self.factsheet_handler.subscribe_to_topics(self.mqtt_client)
            self.state_handler.subscribe_to_topics(self.mqtt_client)
            self.visualization_subscriber.subscribe_to_topics(self.mqtt_client)

            self.publish_instant_actions()
            self.publish_order()
        else:
            self.logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
            
    
    def publish_instant_actions(self):
        self.instant_actions_publisher.add_action(
            action_name="PICK",
            action_id="action_002",
            blocking_type="HARD",
            action_parameters=[
                {"key": "duration", "value": 10},
                {"key": "direction", "value": "right"}
            ]
        )

        self.instant_actions_publisher.update_action(
            index=0,
            action_name="DROP",
            action_parameters=[
                {"key": "duration", "value": 15},
                {"key": "height", "value": "low"}
            ]
        )

        self.instant_actions_publisher.publish_instant_actions(self.mqtt_client)
        
        
    def publish_order(self):
        self.order_publisher.add_node(
            node_id="node_1",
            sequence_id=1,
            node_description="Starting node",
            node_position={
                "x": 0.0,
                "y": 0.0,
                "theta": 0.0,
                "mapId": "map_1",
                "allowedDeviationXy": 0.1,
                "allowedDeviationTheta": 0.1,
                "mapDescription": "Ground floor"
            },
            actions=[
                {
                    "actionId": "action_1",
                    "actionType": "PICK",
                    "actionDescription": "Picking up load",
                    "blockingType": "HARD",
                    "actionParameters": [
                        {"key": "duration", "value": 5},
                        {"key": "direction", "value": "left"}
                    ]
                }
            ]
        )

        self.order_publisher.add_edge(
            edge_id="edge_1",
            sequence_id=1,
            start_node_id="node_1",
            end_node_id="node_2",
            edge_description="Edge from node 1 to node 2",
            actions=[],
            maxSpeed=1.5,
            orientation=0.0,
            rotationAllowed=True,
            length=10.0
        )

        self.order_publisher.publish_order(self.mqtt_client)

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        try:
            message = json.loads(payload)
            self.logger.info(f"Received message: {message}")

            if "connection" in msg.topic:
                self.connection_handler.validate_message(message)
                self.connection_handler.process_connection_message(message)
            elif "factsheet" in msg.topic:
                self.factsheet_handler.validate_message(message)
                self.factsheet_handler.process_factsheet_message(message)
            elif "instantActions" in msg.topic:
                self.logger.info(f"Processing instant actions: {message}")
            elif "state" in msg.topic:
                self.state_handler.validate_message(message)
                self.state_handler.process_state_message(message)
            elif "visualization" in msg.topic:
                self.visualization_subscriber.validate_message(message)
                self.visualization_subscriber.process_visualization_message(message)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON message: {e}")
        except jsonschema.exceptions.ValidationError:
            pass

if __name__ == '__main__':
    fleet_manager = FleetManager()
    fleet_manager.mqtt_client.loop_forever()
