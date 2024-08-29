import json
import psycopg2
import os
import paho.mqtt.client as mqtt
import logging
from submodules.connection import ConnectionHandler
from submodules.factsheet import FactsheetHandler
from submodules.instant_actions import InstantActionsPublisher
from submodules.order import OrderPublisher
from submodules.state import StateHandler
from submodules.visualization import VisualizationSubscriber
from submodules.first_table import CreateDatabaseAndTables
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
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        fleet_info = config['fleet_info']
        self.fleetname = fleet_info['fleetname']
        self.version = fleet_info['version']
        self.versions = fleet_info['versions']
        self.manufacturer = fleet_info['manufacturer']
        
        # PostgreSQL bağlantısı
        postgres_config = config['postgres']
        try:
            self.conn = psycopg2.connect(
                host=postgres_config['host'],
                port=postgres_config['port'],
                database=postgres_config['database'],
                user=postgres_config['user'],
                password=postgres_config['password']
            )
            self.cursor = self.conn.cursor()
            self.logger.info("Connected to PostgreSQL database successfully.")
            CreateDatabaseAndTables(self.conn, postgres_config['database'])
        except Exception as e:
            self.logger.error(f"Failed to connect to PostgreSQL database: {e}")
            self.conn = None

        self.connection_handler = ConnectionHandler(self.fleetname, self.version, self.versions, self.conn)
        self.factsheet_handler = FactsheetHandler(self.fleetname, self.version , self.versions,self.conn)
        self.instant_actions_publisher = InstantActionsPublisher(self.fleetname, self.version, self.versions, self.manufacturer, "001", self.conn)
        self.order_publisher = OrderPublisher(self.fleetname, self.version, self.versions, self.manufacturer, "001",self.conn)
        self.state_handler = StateHandler(self.fleetname, self.version, self.versions,self.conn)
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
        
    def handle_connection_message(self, message):
        self.connection_handler.process_connection_message(message)

    def handle_factsheet_message(self, message):
        self.factsheet_handler.process_factsheet_message(message)

    def handle_instant_actions_message(self, message):
        self.logger.info(f"Processing instant actions: {message}")

    def handle_state_message(self, message):
        self.state_handler.process_state_message(message)
        battery_status = self.state_handler.get_battery_status(message)
        print("Battery Status:", battery_status)

        agv_position = self.state_handler.get_agv_position(message)
        print("AGV Position:", agv_position)

        emergency_status = self.state_handler.get_emergency_status(message)
        print("Emergency Status:", emergency_status)
        
        velocity = self.state_handler.get_velocity(message)
        print("Velocity:", velocity)
        
        action_states = self.state_handler.get_action_states(message)
        print("Action States:", action_states)
        
        operating_mode = self.state_handler.get_operating_mode(message)
        print("Operating Mode:", operating_mode)
        
        driving_status = self.state_handler.get_driving_status(message)
        print("Driving Status:", driving_status)
        
        paused_status = self.state_handler.get_paused_status(message)
        print("Paused Status:", paused_status)
        
        last_node_id = self.state_handler.get_last_node_id(message)
        print("Last Node ID:", last_node_id)
        
        last_node_sequence_id = self.state_handler.get_last_node_sequence_id(message)
        print("Last Node Sequence ID:", last_node_sequence_id)

        robot_id = self.state_handler.get_robot_id(message)
        print("Robot ID:", robot_id)

    def handle_visualization_message(self, message):
        self.visualization_subscriber.process_visualization_message(message)

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        try:
            message = json.loads(payload)

            if "connection" in msg.topic:
                self.handle_connection_message(message)
            elif "factsheet" in msg.topic:
                self.handle_factsheet_message(message)
            elif "instantActions" in msg.topic:
                self.handle_instant_actions_message(message)
            elif "state" in msg.topic:
                self.handle_state_message(message)
            elif "visualization" in msg.topic:
                self.handle_visualization_message(message)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON message: {e}")
        except jsonschema.exceptions.ValidationError:
            pass
        

if __name__ == '__main__':
    fleet_manager = FleetManager()
    fleet_manager.mqtt_client.loop_forever()
