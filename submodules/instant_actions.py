import json
import datetime
import logging

class InstantActionsPublisher:
    def __init__(self, fleetname, version, versions, manufacturer, robot_id):
        self.fleetname = fleetname
        self.version = version
        self.manufacturer = manufacturer
        self.robot_id = robot_id
        self.versions = versions
        
        self.logger = logging.getLogger('InstantActionsPublisher')
        logging.basicConfig(level=logging.INFO)

        """Instant actions mesajını oluşturur."""
        self.message_template = {
            "headerId": 1,
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

    def publish_instant_actions(self, mqtt_client):
        """Instant actions mesajını MQTT üzerinden yayınlar."""
        self._update_timestamp()
        message = json.dumps(self.message_template)
        topic = f"{self.fleetname}/{self.versions}/{self.manufacturer}/{self.robot_id}/instantActions"
        mqtt_client.publish(topic, message, qos=1, retain=False)
        self.logger.info(f"Instant actions message published.")

    def subscribe_to_topics(self, mqtt_client):
        """Instant actions ile ilgili konulara abone olur."""
        topic = f"{self.fleetname}/{self.versions}/+/+/instantActions"
        mqtt_client.subscribe(topic, qos=1)
        self.logger.info(f"Subscribed to instant actions topic: {topic}")


    def add_action(self, action_name, action_id, blocking_type, action_parameters):
        """Yeni bir action ekler."""
        action = {
            "actionName": action_name,
            "actionId": action_id,
            "blockingType": blocking_type,
            "actionParameters": action_parameters
        }
        self.message_template["actions"].append(action)

    def update_action(self, index, action_name=None, action_id=None, blocking_type=None, action_parameters=None):
        """Mevcut bir action'ı günceller."""
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
        """Belirtilen indexteki action'ı siler."""
        try:
            self.message_template["actions"].pop(index)
        except IndexError:
            self.logger.error(f"Action index {index} is out of range.")