import json
import os
import jsonschema
from jsonschema import validate
import logging

class FactsheetHandler:
    def __init__(self, fleetname, version, versions, db_conn):
        self.fleetname = fleetname
        self.version = version
        self.versions = versions
        self.db_conn = db_conn  

        self.logger = logging.getLogger("FactsheetHandler")
        logging.basicConfig(level=logging.INFO)

        schema_path = os.path.join(
            os.path.dirname(__file__), "schemas", "factsheet.schema"
        )
        with open(schema_path, "r", encoding="utf-8") as schema_file:
            self.factsheet_schema = json.load(schema_file)

    def validate_message(self, message):
        try:
            validate(instance=message, schema=self.factsheet_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.logger.error(f"Factsheet schema validation failed: {e.message}")
            raise

    def process_factsheet_message(self, message):
        self.validate_message(message)
        try:
            header_id = message.get("headerId", 0)
            timestamp = message.get("timestamp")
            version = message.get("version")
            manufacturer = message.get("manufacturer", "UNKNOWN")
            serial_number = message.get("serialNumber", "UNKNOWN")
            series_name = message["typeSpecification"].get("seriesName", "")
            agv_kinematic = message["typeSpecification"].get("agvKinematic", "")
            agv_class = message["typeSpecification"].get("agvClass", "")
            max_load_mass = message["typeSpecification"].get("maxLoadMass", 0)
            localization_types = message["typeSpecification"].get(
                "localizationTypes", []
            )
            navigation_types = message["typeSpecification"].get("navigationTypes", [])
            speed_min = message["physicalParameters"].get("speedMin", 0.0)
            speed_max = message["physicalParameters"].get("speedMax", 0.0)
            acceleration_max = message["physicalParameters"].get("accelerationMax", 0.0)
            deceleration_max = message["physicalParameters"].get("decelerationMax", 0.0)
            height_min = message["physicalParameters"].get("heightMin", 0.0)
            height_max = message["physicalParameters"].get("heightMax", 0.0)
            width = message["physicalParameters"].get("width", 0.0)
            length = message["physicalParameters"].get("length", 0.0)

            msg_len = message["protocolLimits"]["maxStringLens"].get("msgLen", 0)
            topic_serial_len = message["protocolLimits"]["maxStringLens"].get(
                "topicSerialLen", 0
            )
            topic_element_len = message["protocolLimits"]["maxStringLens"].get(
                "topicElemLen", 0
            )
            idLen = message["protocolLimits"]["maxStringLens"].get("idLen", 0)
            idNumericalOnly = message["protocolLimits"]["maxStringLens"].get(
                "idNumericalOnly", 0
            )
            enumLen = message["protocolLimits"]["maxStringLens"].get("enumLen", 0)
            loadIdLen = message["protocolLimits"]["maxStringLens"].get("loadIdLen", 0)

            orderNodes = message["protocolLimits"]["maxArrayLens"].get("order.nodes", 0)
            orderEdges = message["protocolLimits"]["maxArrayLens"].get("order.edges", 0)
            nodeActions = message["protocolLimits"]["maxArrayLens"].get(
                "node.actions", 0
            )
            edgeActions = message["protocolLimits"]["maxArrayLens"].get(
                "edge.actions", 0
            )
            actionsActionsParameters = message["protocolLimits"]["maxArrayLens"].get(
                "actions.actionsParameters", 0
            )
            instantActions = message["protocolLimits"]["maxArrayLens"].get(
                "instantActions", 0
            )
            trajectoryKnotVector = message["protocolLimits"]["maxArrayLens"].get(
                "trajectory.knotVector", 0
            )
            trajectoryControlPoints = message["protocolLimits"]["maxArrayLens"].get(
                "trajectory.controlPoints", 0
            )
            stateNodeStates = message["protocolLimits"]["maxArrayLens"].get(
                "state.nodeStates", 0
            )
            stateEdgeStates = message["protocolLimits"]["maxArrayLens"].get(
                "state.edgeStates", 0
            )
            stateLoads = message["protocolLimits"]["maxArrayLens"].get("state.loads", 0)
            stateActionStates = message["protocolLimits"]["maxArrayLens"].get(
                "state.actionStates", 0
            )
            stateErrors = message["protocolLimits"]["maxArrayLens"].get(
                "state.errors", 0
            )
            stateInformation = message["protocolLimits"]["maxArrayLens"].get(
                "state.information", 0
            )
            errorErrorReferences = message["protocolLimits"]["maxArrayLens"].get(
                "error.errorReferences", 0
            )
            informationInfoReferences = message["protocolLimits"]["maxArrayLens"].get(
                "information.infoReferences", 0
            )

            minOrderInterval = message["protocolLimits"]["timing"].get(
                "minOrderInterval", 0.0
            )
            minStateInterval = message["protocolLimits"]["timing"].get(
                "minStateInterval", 0.0
            )
            defaultStateInterval = message["protocolLimits"]["timing"].get(
                "defaultStateInterval", 0.0
            )
            visualizationInterval = message["protocolLimits"]["timing"].get(
                "visualizationInterval", 0.0
            )
            protocol_features = message.get("protocolFeatures", {})   
            optionalParameters = protocol_features.get("optionalParameters", [])
            agvActions = protocol_features.get("agvActions", [])
            
            agvGeometry = message.get("agvGeometry", {})  
            wheelDefinitions = agvGeometry.get("wheelDefinitions", [])
            enveloes2d = agvGeometry.get("envelopes2d", []) 
            
            loadSpecification = message.get("loadSpecification", {})
            loadPositions = message["loadSpecification"].get(
                "loadPositions", None
            )
            loadSets = loadSpecification.get("loadSets", [])

            
            cursor = self.db_conn.cursor()
            insert_query = """
                INSERT INTO factsheet (
                    header_id, timestamp, version, manufacturer, serial_number, series_name,
                    agv_kinematic, agv_class, max_load_mass, localization_types, navigation_types,
                    speed_min, speed_max, acceleration_max, deceleration_max, height_min, height_max,
                    width, length, msg_len, topic_serial_len, topic_elem_len, id_len, id_numerical_only, enum_len, load_id_len,
                    order_nodes_max, node_actions_max, order_edges_max, edge_actions_max, actions_parameters_max, instant_actions_max, trajectory_knot_vector_max, 
                    trajectory_control_points_max, state_node_states_max, state_edge_states_max, state_loads_max, state_action_states_max, 
                    state_errors_max, state_information_max, error_references_max, information_references_max, min_order_interval, 
                    min_state_interval, default_state_interval, visualization_interval, optional_parameters, agv_actions, wheel_definitions, envelopes_2d, load_positions, load_sets
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            data_tuple = (
                header_id,
                timestamp,
                version,
                manufacturer,
                serial_number,
                series_name,
                agv_kinematic,
                agv_class,
                max_load_mass,
                localization_types,
                navigation_types,
                speed_min,
                speed_max,
                acceleration_max,
                deceleration_max,
                height_min,
                height_max,
                width,
                length,
                msg_len,
                topic_serial_len,
                topic_element_len,
                idLen,
                idNumericalOnly,
                enumLen,
                loadIdLen,
                orderNodes,
                nodeActions,
                orderEdges,
                edgeActions,
                actionsActionsParameters,
                instantActions,
                trajectoryKnotVector,
                trajectoryControlPoints,
                stateNodeStates,
                stateEdgeStates,
                stateLoads,
                stateActionStates,
                stateErrors,
                stateInformation,
                errorErrorReferences,
                informationInfoReferences,
                minOrderInterval,
                minStateInterval,
                defaultStateInterval,
                visualizationInterval,
                json.dumps(optionalParameters),
                json.dumps(agvActions),
                json.dumps(wheelDefinitions),
                json.dumps(enveloes2d),
                loadPositions,
                json.dumps(loadSets)
            )

            cursor.execute(insert_query, data_tuple)
            self.db_conn.commit()  

            self.logger.info(
                f"Factsheet data inserted into database for serial number: {serial_number}"
            )

        except Exception as e:
            self.logger.error(f"Failed to insert factsheet data into database: {e}")
            self.db_conn.rollback()  
            
    def subscribe_to_topics(self, mqtt_client):
        topic = f"{self.fleetname}/{self.versions}/+/+/factsheet"
        mqtt_client.subscribe(topic, qos=0)
        self.logger.info(f"Subscribed to topic: {topic}")
        
        
    def get_robot_id(self, message):
        return message.get("serialNumber", "UNKNOWN")
    
    def get_header_id(self, message):
        return message.get("headerId", 0)
    
    def get_timestamp(self, message):
        return message.get("timestamp")
    
    def get_version(self, message):
        return message.get("version", "UNKNOWN")
    
    def get_manufacturer(self, message):
        return message.get("manufacturer", "UNKNOWN")
    
    def get_series_name(self, message):
        return message["typeSpecification"].get("seriesName", "")
    
    def get_agv_kinematic(self, message):
        return message["typeSpecification"].get("agvKinematic", "")
    
    def get_agv_class(self, message):
        return message["typeSpecification"].get("agvClass", "")
    
    def get_max_load_mass(self, message):
        return message["typeSpecification"].get("maxLoadMass", 0)
    
    def get_localization_types(self, message):
        return message["typeSpecification"].get("localizationTypes", [])
    
    def get_navigation_types(self, message):
        return message["typeSpecification"].get("navigationTypes", [])
    
    def get_speed_min(self, message):
        return message["physicalParameters"].get("speedMin", 0.0)
    
    def get_speed_max(self, message):
        return message["physicalParameters"].get("speedMax", 0.0)
    
    def get_acceleration_max(self, message):
        return message["physicalParameters"].get("accelerationMax", 0.0)
    
    def get_deceleration_max(self, message):
        return message["physicalParameters"].get("decelerationMax", 0.0)
    
    def get_height_min(self, message):
        return message["physicalParameters"].get("heightMin", 0.0)
    
    def get_height_max(self, message):
        return message["physicalParameters"].get("heightMax", 0.0)
    
    def get_width(self, message):
        return message["physicalParameters"].get("width", 0.0)
    
    def get_length(self, message):
        return message["physicalParameters"].get("length", 0.0)
    
    def get_msg_len(self, message):
        return message["protocolLimits"]["maxStringLens"].get("msgLen", 0)
    
    def get_topic_serial_len(self, message):
        return message["protocolLimits"]["maxStringLens"].get("topicSerialLen", 0)
    
    def get_topic_element_len(self, message):
        return message["protocolLimits"]["maxStringLens"].get("topicElemLen", 0)
    
    def get_id_len(self, message):
        return message["protocolLimits"]["maxStringLens"].get("idLen", 0)
    
    def get_id_numerical_only(self, message):
        return message["protocolLimits"]["maxStringLens"].get("idNumericalOnly", 0)
    
    def get_enum_len(self, message):
        return message["protocolLimits"]["maxStringLens"].get("enumLen", 0)
    
    def get_load_id_len(self, message):
        return message["protocolLimits"]["maxStringLens"].get("loadIdLen", 0)
    
    def get_order_nodes_max(self, message):
        return message["protocolLimits"]["maxArrayLens"].get("order.nodes", 0)
    
    def get_node_actions_max(self, message):
        return message["protocolLimits"]["maxArrayLens"].get("node.actions", 0)
    
    def get_order_edges_max(self, message):
        return message["protocolLimits"]["maxArrayLens"].get("order.edges", 0)
    
    def get_edge_actions_max(self, message):
        return message["protocolLimits"]["maxArrayLens"].get("edge.actions", 0)
    
    def get_actions_parameters_max(self, message):
        return message["protocolLimits"]["maxArrayLens"].get("actions.actionsParameters", 0)
    
    def get_instant_actions_max(self, message):
        return message["protocolLimits"]["maxArrayLens"].get("instantActions", 0)
    
    def get_trajectory_knot_vector_max(self, message):
        return message["protocolLimits"]["maxArrayLens"].get("trajectory.knotVector", 0)
    
    def get_trajectory_control_points_max(self, message):
        return message["protocolLimits"]["maxArrayLens"].get("trajectory.controlPoints", 0)
    
    def get_state_node_states_max(self, message):
        return message["protocolLimits"]["maxArrayLens"].get("state.nodeStates", 0)
    
    def get_state_edge_states_max(self, message):
        return message["protocolLimits"]["maxArrayLens"].get("state.edgeStates", 0)
    
    def get_state_loads_max(self, message):
        return message["protocolLimits"]["maxArrayLens"].get("state.loads", 0)
    
    def get_state_action_states_max(self, message):
        return message["protocolLimits"]["maxArrayLens"].get("state.actionStates", 0)
    
    def get_state_errors_max(self, message):
        return message["protocolLimits"]["maxArrayLens"].get("state.errors", 0)
    
    def get_state_information_max(self, message):
        return message["protocolLimits"]["maxArrayLens"].get("state.information", 0)
    
    def get_error_references_max(self, message):
        return message["protocolLimits"]["maxArrayLens"].get("error.errorReferences", 0)
    
    def get_information_references_max(self, message):
        return message["protocolLimits"]["maxArrayLens"].get("information.infoReferences", 0)
    
    def get_min_order_interval(self, message):
        return message["protocolLimits"]["timing"].get("minOrderInterval", 0.0)
    
    def get_min_state_interval(self, message):
        return message["protocolLimits"]["timing"].get("minStateInterval", 0.0)
    
    def get_default_state_interval(self, message):
        return message["protocolLimits"]["timing"].get("defaultStateInterval", 0.0)
    
    def get_visualization_interval(self, message):
        return message["protocolLimits"]["timing"].get("visualizationInterval", 0.0)
    
    def get_protocol_features(self, message):
        return message.get("protocolFeatures", {})
    
    def get_optional_parameters(self, message):
        protocol_features = self.get_protocol_features(message)
        return protocol_features.get("optionalParameters", [])
    
    def get_agv_actions(self, message):
        protocol_features = self.get_protocol_features(message)
        return protocol_features.get("agvActions", [])
    
    def get_agv_geometry(self, message):
        return message.get("agvGeometry", {})
    
    def get_wheel_definitions(self, message):
        agv_geometry = self.get_agv_geometry(message)
        return agv_geometry.get("wheelDefinitions", [])
    
    def get_envelopes_2d(self, message):
        agv_geometry = self.get_agv_geometry(message)
        return agv_geometry.get("envelopes2d", [])
    
    def get_load_specification(self, message):
        return message.get("loadSpecification", {})
    
    def get_load_positions(self, message):
        load_specification = self.get_load_specification(message)
        return load_specification.get("loadPositions", None)
    
    def get_load_sets(self, message):
        load_specification = self.get_load_specification(message)
        return load_specification.get("loadSets", [])
    
    
