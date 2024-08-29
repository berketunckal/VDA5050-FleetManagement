import json
import os
import logging
import datetime
from jsonschema import validate, ValidationError

class StateHandler:
    def __init__(self, fleetname, version, versions, db_conn):
        self.fleetname = fleetname
        self.version = version
        self.versions = versions
        self.db_conn = db_conn 

        self.logger = logging.getLogger('StateHandler')
        logging.basicConfig(level=logging.WARN)

        schema_path = os.path.join(os.path.dirname(__file__), 'schemas', 'state.schema')
        with open(schema_path, 'r', encoding="utf-8") as schema_file:
            self.state_schema = json.load(schema_file)

    def subscribe_to_topics(self, mqtt_client):
        topic = f"{self.fleetname}/{self.versions}/+/+/state"
        mqtt_client.subscribe(topic, qos=0)
        self.logger.info(f"Subscribed to state topic: {topic}")

    def validate_message(self, message):
        try:
            validate(instance=message, schema=self.state_schema)
        except ValidationError as e:
            self.logger.error(f"State schema validation failed: {e.message}")
            raise

    def _save_to_database(self, message):
        try:
            cursor = self.db_conn.cursor()
            insert_query = """
                INSERT INTO state (
                    header_id, timestamp, version, manufacturer, serial_number, order_id, order_update_id, zone_set_id,
                    last_node_id, last_node_sequence_id, driving, paused, new_base_request, distance_since_last_node,
                    operating_mode, node_states, edge_states, agv_position, velocity, loads, action_states, battery_state,
                    errors, information, safety_state
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                message.get("headerId"),
                datetime.datetime.now(),
                message.get("version"),
                message.get("manufacturer"),
                message.get("serialNumber"),
                message.get("orderId"),
                message.get("orderUpdateId"),
                message.get("zoneSetId"),
                message.get("lastNodeId"),
                message.get("lastNodeSequenceId"),
                message.get("driving"),
                message.get("paused"),
                message.get("newBaseRequest"),
                message.get("distanceSinceLastNode"),
                message.get("operatingMode"),
                json.dumps(message.get("nodeStates")),
                json.dumps(message.get("edgeStates")),
                json.dumps(message.get("agvPosition")),
                json.dumps(message.get("velocity")),
                json.dumps(message.get("loads")),
                json.dumps(message.get("actionStates")),
                json.dumps(message.get("batteryState")),
                json.dumps(message.get("errors")),
                json.dumps(message.get("information")),
                json.dumps(message.get("safetyState"))
            ))
            self.db_conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to save state data to database: {e}")
            self.db_conn.rollback()

    def process_state_message(self, message):
        try:
            self.validate_message(message)  
            self._save_to_database(message)
        except ValidationError:
            self.logger.error("State message validation failed. Skipping database save.")
            
            
    def get_battery_status(self, state_message):
        battery_state = state_message.get("batteryState", {})
        return {
            "batteryCharge": battery_state.get("batteryCharge", 0),
            "batteryVoltage": battery_state.get("batteryVoltage", 0.0),
            "batteryHealth": battery_state.get("batteryHealth", 0),
            "charging": battery_state.get("charging", False),
            "reach": battery_state.get("reach", 0)
        }
    
    def get_robot_id(self, state_message):
        return state_message.get("serialNumber", "")
    
    def get_order_id(self, state_message):
        return state_message.get("orderId", "")
    
    def get_order_update_id(self, state_message):
        return state_message.get("orderUpdateId", "")
    
    def get_zone_set_id(self, state_message):
        return state_message.get("zoneSetId", "")
    
    def get_last_node_id(self, state_message):
        return state_message.get("lastNodeId", "")

    def get_last_node_sequence_id(self, state_message):
        return state_message.get("lastNodeSequenceId", 0)

    def get_driving_status(self, state_message):
        return state_message.get("driving", False)

    def get_paused_status(self, state_message):
        return state_message.get("paused", False)

    def get_new_base_request(self, state_message):
        return state_message.get("newBaseRequest", False)
    
    def get_distance_since_last_node(self, state_message):
        return state_message.get("distanceSinceLastNode", 0.0)
    
    def get_operating_mode(self, state_message):
        return state_message.get("operatingMode", "UNKNOWN")
    
    def get_node_states(self, state_message):
        return state_message.get("nodeStates", [])
    
    def get_edge_states(self, state_message):
        return state_message.get("edgeStates", [])
    
    def get_agv_position(self, state_message):
        return state_message.get("agvPosition", {})
    
    def get_velocity(self, state_message):
        return state_message.get("velocity", {})

    def get_loads(self, state_message):
        return state_message.get("loads", [])
    
    def get_action_states(self, state_message):
        return state_message.get("actionStates", [])
    
    def get_errors(self, state_message):
        return state_message.get("errors", [])
    
    def get_information(self, state_message):
        return state_message.get("information", [])
    
    def get_emergency_status(self, state_message):
        safety_state = state_message.get("safetyState", {})
        return safety_state.get("eStop", "NONE")
    
    def get_field_violation(self, state_message):
        safety_state = state_message.get("safetyState", {})
        return safety_state.get("fieldViolation", "false")






