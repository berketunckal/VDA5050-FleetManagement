import json
import datetime
import logging

class OrderPublisher:
    def __init__(self, fleetname, version, versions, manufacturer, db_conn):
        self.fleetname = fleetname
        self.version = version
        self.manufacturer = manufacturer
        self.versions = versions
        self.db_conn = db_conn  

        self.logger = logging.getLogger('OrderPublisher')
        logging.basicConfig(level=logging.WARN)

        # Header ID'yi veritabanından yükle
        self.message_template = {
            "headerId": self._load_last_header_id_from_db(),
            "timestamp": None,
            "version": self.version,
            "manufacturer": self.manufacturer,
            "serialNumber": None,
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

    def _load_last_header_id_from_db(self):
        """Veritabanından en son kullanılan headerId'yi yükler."""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT MAX(header_id) FROM orders")
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
        except Exception as e:
            self.logger.error(f"Failed to save data to database: {e}")
            self.db_conn.rollback()

    def publish_order(self, mqtt_client, robot_id):
        self._update_timestamp()
        self.robot_id = robot_id
        self.message_template["serialNumber"] = robot_id        
        message = json.dumps(self.message_template)
        topic = f"{self.fleetname}/{self.versions}/{self.manufacturer}/{robot_id}/order"
        mqtt_client.publish(topic, message, qos=0, retain=False)
        self._save_to_database()
        self.logger.info(f"Order message published.")

    def add_node(self, node_id, sequence_id, node_description, node_position, actions, released=True):
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
        try:
            node = self.message_template["nodes"][index]
            for key, value in kwargs.items():
                if key in node:
                    node[key] = value
        except IndexError:
            self.logger.error(f"Node index {index} is out of range.")

    def remove_node(self, index):
        try:
            self.message_template["nodes"].pop(index)
        except IndexError:
            self.logger.error(f"Node index {index} is out of range.")

    def add_edge(self, edge_id, sequence_id, start_node_id, end_node_id, edge_description, actions, **kwargs):
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
        try:
            edge = self.message_template["edges"][index]
            for key, value in kwargs.items():
                if key in edge:
                    edge[key] = value
        except IndexError:
            self.logger.error(f"Edge index {index} is out of range.")

    def remove_edge(self, index):
        try:
            self.message_template["edges"].pop(index)
        except IndexError:
            self.logger.error(f"Edge index {index} is out of range.")
