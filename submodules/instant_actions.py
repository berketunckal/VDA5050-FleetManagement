import json
import datetime
import logging

class InstantActionsPublisher:
    def __init__(self, fleetname, version, versions, manufacturer, robot_id, db_conn):
        self.fleetname = fleetname
        self.version = version
        self.manufacturer = manufacturer
        self.robot_id = robot_id
        self.versions = versions
        self.db_conn = db_conn  
        
        self.logger = logging.getLogger('InstantActionsPublisher')
        logging.basicConfig(level=logging.INFO)

        # Header ID'yi veritabanından yükle
        self.message_template = {
            "headerId": self._load_last_header_id_from_db(),
            "timestamp": None,
            "version": self.version,
            "manufacturer": self.manufacturer,
            "serialNumber": self.robot_id,
            "actions": [
                {
                    "actionName": "PICK",
                    "actionId": "action_001",
                    "blockingType": "HARD",
                    "actionParameters": [
                        {"key": "duration", "value": 5},
                        {"key": "direction", "value": "left"}
                    ]
                }
            ]
        }

    def _load_last_header_id_from_db(self):
        """Veritabanından en son kullanılan headerId'yi yükler."""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT MAX(header_id) FROM instant_actions")
            last_header_id = cursor.fetchone()[0]
            return last_header_id if last_header_id is not None else 0
        except Exception as e:
            self.logger.error(f"Failed to load last headerId from database: {e}")
            return 0

    def _update_timestamp(self):
        self.message_template["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    def _increment_header_id(self):
        self.message_template["headerId"] += 1

    def _save_to_database(self):
        self._increment_header_id() 
        self._update_timestamp()  
        
        try:
            cursor = self.db_conn.cursor()
            insert_query = """
                INSERT INTO instant_actions (header_id, timestamp, version, manufacturer, serial_number, actions)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                self.message_template["headerId"],
                datetime.datetime.now(),
                self.version,
                self.manufacturer,
                self.robot_id,
                json.dumps(self.message_template["actions"])
            ))

            self.db_conn.commit()
            self.logger.info(f"Data saved to database with headerId {self.message_template['headerId']}.")
        except Exception as e:
            self.logger.error(f"Failed to save data to database: {e}")
            self.db_conn.rollback()

    def publish_instant_actions(self, mqtt_client):
        self._update_timestamp()
        message = json.dumps(self.message_template)
        topic = f"{self.fleetname}/{self.versions}/{self.manufacturer}/{self.robot_id}/instantActions"
        mqtt_client.publish(topic, message, qos=0, retain=False)
        self._save_to_database()  # Veritabanına kaydet
        self.logger.info(f"Instant actions message published.")

    def add_action(self, action_name, action_id, blocking_type, action_parameters):
        action = {
            "actionName": action_name,
            "actionId": action_id,
            "blockingType": blocking_type,
            "actionParameters": action_parameters
        }
        self.message_template["actions"].append(action)

    def update_action(self, index, action_name=None, action_id=None, blocking_type=None, action_parameters=None):
        try:
            action = self.message_template["actions"][index]
            if action_name:
                action["actionName"] = action_name
            if action_id:
                action["actionId"] = action_id
            if blocking_type:
                action["blockingType"] = blocking_type
            if action_parameters:
                action["actionParameters"] = action_parameters
        except IndexError:
            self.logger.error(f"Action index {index} is out of range.")

    def remove_action(self, index):
        try:
            self.message_template["actions"].pop(index)
        except IndexError:
            self.logger.error(f"Action index {index} is out of range.")
