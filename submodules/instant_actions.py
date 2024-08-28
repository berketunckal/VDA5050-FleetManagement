import json
import datetime
import logging
import psycopg2

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

        """Instant actions mesajını oluşturur."""
        self.message_template = {
            "headerId": 0,
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

    def _update_timestamp(self):
        """Zaman damgasını günceller."""
        self.message_template["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    def _increment_header_id(self):
        """Header ID'yi artırır."""
        self.message_template["headerId"] += 1

    def _save_to_database(self):
        """Veritabanına yeni bir kayıt ekler."""
        self._increment_header_id()  # Her işlemde headerId artırılıyor
        self._update_timestamp()  # Zaman damgası güncelleniyor
        
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
        """Instant actions mesajını MQTT üzerinden yayınlar."""
        self._update_timestamp()
        message = json.dumps(self.message_template)
        topic = f"{self.fleetname}/{self.versions}/{self.manufacturer}/{self.robot_id}/instantActions"
        mqtt_client.publish(topic, message, qos=0, retain=False)
        self._save_to_database()  # Veritabanına kaydet
        self.logger.info(f"Instant actions message published.")

    def add_action(self, action_name, action_id, blocking_type, action_parameters):
        """Yeni bir action ekler ve veritabanına kaydeder."""
        action = {
            "actionName": action_name,
            "actionId": action_id,
            "blockingType": blocking_type,
            "actionParameters": action_parameters
        }
        self.message_template["actions"].append(action)

    def update_action(self, index, action_name=None, action_id=None, blocking_type=None, action_parameters=None):
        """Mevcut bir action'ı günceller ve veritabanına yeni bir kayıt ekler."""
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
        """Belirtilen indexteki action'ı siler ve veritabanına yeni bir kayıt ekler."""
        try:
            self.message_template["actions"].pop(index)
        except IndexError:
            self.logger.error(f"Action index {index} is out of range.")
