import json
import os
import jsonschema
from jsonschema import validate
import logging

class ConnectionHandler:
    def __init__(self, fleetname, version, versions, db_conn):
        self.fleetname = fleetname
        self.version = version
        self.versions = versions
        self.db_conn = db_conn

        self.logger = logging.getLogger('ConnectionHandler')
        logging.basicConfig(level=logging.INFO)

        schema_path = os.path.join(os.path.dirname(__file__), 'schemas', 'connection.schema')
        with open(schema_path, 'r') as schema_file:
            self.connection_schema = json.load(schema_file)

    def validate_message(self, message):
        try:
            validate(instance=message, schema=self.connection_schema)
            self.logger.info("Message is valid according to the schema.")
        except jsonschema.exceptions.ValidationError as e:
            self.logger.error(f"Schema validation failed: {e.message}")
            raise

    def process_connection_message(self, message):
        connection_state = message.get("connectionState", "CONNECTIONBROKEN")
        agv_id = message.get("serialNumber", "CONNECTIONBROKEN")
        self.logger.info(f"AGV {agv_id} is now {connection_state}")
        self.write_to_database(message)

    def subscribe_to_topics(self, mqtt_client):
        topic = f"{self.fleetname}/{self.versions}/+/+/connection"
        mqtt_client.subscribe(topic, qos=1)
        self.logger.info(f"Subscribed to topic: {topic}")

    def write_to_database(self, message):
        cursor = self.db_conn.cursor()
        try:
            query = """
            INSERT INTO connection (header_id, timestamp, version, manufacturer, serial_number, connection_state)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                message.get("headerId"),
                message.get("timestamp"),
                message.get("version"),
                message.get("manufacturer"),
                message.get("serialNumber"),
                message.get("connectionState")
            ))
            self.db_conn.commit()
            self.logger.info("Connection data written to database successfully.")
        except Exception as e:
            self.logger.error(f"Failed to write to database: {e}")
            self.db_conn.rollback()
