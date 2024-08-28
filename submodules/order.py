import json
import datetime
import logging

class OrderPublisher:
    def __init__(self, fleetname, version, versions, manufacturer, robot_id, db_conn):
        self.fleetname = fleetname
        self.version = version
        self.manufacturer = manufacturer
        self.robot_id = robot_id
        self.versions = versions
        self.db_conn = db_conn  

        self.logger = logging.getLogger('OrderPublisher')
        logging.basicConfig(level=logging.INFO)

        self.message_template = {
            "headerId": 1,
            "timestamp": None,
            "version": self.version,
            "manufacturer": self.manufacturer,
            "serialNumber": self.robot_id,
            "orderId": "order_001",
            "orderUpdateId": 0,
            "zoneSetId": "zone_set_001",
            "nodes": [
                {
                    "nodeId": "node_1",
                    "sequenceId": 1,
                    "nodeDescription": "First node",
                    "released": True,
                    "nodePosition": {
                        "x": 0.0,
                        "y": 0.0,
                        "theta": 0.0,
                        "mapId": "map_1",
                        "allowedDeviationXy": 0.1,
                        "allowedDeviationTheta": 0.1,
                        "mapDescription": "Ground floor"
                    },
                    "actions": [
                        {
                            "actionId": "action_1",
                            "actionType": "PICK",
                            "actionDescription": "Picking up the load",
                            "blockingType": "HARD",
                            "actionParameters": [
                                {"key": "duration", "value": 5},
                                {"key": "direction", "value": "left"}
                            ]
                        }
                    ]
                }
            ],
            "edges": [
                {
                    "edgeId": "edge_1",
                    "sequenceId": 2,
                    "edgeDescription": "Edge to node 2",
                    "released": True,
                    "startNodeId": "node_1",
                    "endNodeId": "node_2",
                    "maxSpeed": 1.5,
                    "maxHeight": 2.0,
                    "minHeight": 0.5,
                    "orientation": 0.0,
                    "direction": "straight",
                    "rotationAllowed": True,
                    "maxRotationSpeed": 0.5,
                    "length": 10.0,
                    "trajectory": {
                        "degree": 3,
                        "knotVector": [0, 0, 0, 1, 1, 1],
                        "controlPoints": [
                            {"x": 0.0, "y": 0.0, "weight": 1.0},
                            {"x": 5.0, "y": 0.0, "weight": 1.0},
                            {"x": 10.0, "y": 0.0, "weight": 1.0}
                        ]
                    },
                    "actions": []
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
                INSERT INTO orders (header_id, timestamp, version, manufacturer, serial_number, order_id, zone_set_id, order_update_id, nodes, edges)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                self.message_template["headerId"],
                datetime.datetime.now(),
                self.version,
                self.manufacturer,
                self.robot_id,
                self.message_template["orderId"],
                self.message_template["zoneSetId"],
                self.message_template["orderUpdateId"],
                json.dumps(self.message_template["nodes"]),
                json.dumps(self.message_template["edges"]),
                    ))

            self.db_conn.commit()
            self.logger.info(f"Data saved to database with headerId {self.message_template['headerId']}.")
        except Exception as e:
            self.logger.error(f"Failed to save data to database: {e}")
            self.db_conn.rollback()

    def publish_order(self, mqtt_client):
        """Order mesajını MQTT üzerinden yayınlar."""
        self._update_timestamp()
        message = json.dumps(self.message_template)
        topic = f"{self.fleetname}/{self.versions}/{self.manufacturer}/{self.robot_id}/order"
        mqtt_client.publish(topic, message, qos=0, retain=False)
        self._save_to_database()
        self.logger.info(f"Order message published.")

    def add_node(self, node_id, sequence_id, node_description, node_position, actions, released=True):
        """Yeni bir node ekler ve veritabanına kaydeder."""
        node = {
            "nodeId": node_id,
            "sequenceId": sequence_id,
            "nodeDescription": node_description,
            "nodePosition": node_position,
            "actions": actions,
            "released": released
        }
        self.message_template["nodes"].append(node)

    def update_node(self, index, **kwargs):
        """Mevcut bir node'u günceller ve veritabanına kaydeder."""
        try:
            node = self.message_template["nodes"][index]
            for key, value in kwargs.items():
                if key in node:
                    node[key] = value
        except IndexError:
            self.logger.error(f"Node index {index} is out of range.")

    def remove_node(self, index):
        """Belirtilen indexteki node'u siler ve veritabanına kaydeder."""
        try:
            self.message_template["nodes"].pop(index)
        except IndexError:
            self.logger.error(f"Node index {index} is out of range.")

    def add_edge(self, edge_id, sequence_id, start_node_id, end_node_id, edge_description, actions, **kwargs):
        """Yeni bir edge ekler ve veritabanına kaydeder."""
        edge = {
            "edgeId": edge_id,
            "sequenceId": sequence_id,
            "edgeDescription": edge_description,
            "startNodeId": start_node_id,
            "endNodeId": end_node_id,
            "actions": actions,
            **kwargs
        }
        self.message_template["edges"].append(edge)

    def update_edge(self, index, **kwargs):
        """Mevcut bir edge'i günceller ve veritabanına kaydeder."""
        try:
            edge = self.message_template["edges"][index]
            for key, value in kwargs.items():
                if key in edge:
                    edge[key] = value
        except IndexError:
            self.logger.error(f"Edge index {index} is out of range.")

    def remove_edge(self, index):
        """Belirtilen indexteki edge'i siler ve veritabanına kaydeder."""
        try:
            self.message_template["edges"].pop(index)
        except IndexError:
            self.logger.error(f"Edge index {index} is out of range.")