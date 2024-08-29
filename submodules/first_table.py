from psycopg2 import sql

def CreateDatabaseAndTables(conn, dbname):   
    create_database(conn, dbname)
    create_connection_table(conn)
    create_factsheet_table(conn)
    create_instant_actions_table(conn)
    create_order_table(conn)
    create_state_table(conn)

def create_database(conn, dbname):
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{dbname}';")
    if not cursor.fetchone():
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
        print(f"Veritabanı '{dbname}' başarıyla oluşturuldu.")


def create_connection_table(conn):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'connection'
        );
    """)
    if not cursor.fetchone()[0]:
        cursor.execute("""
            CREATE TABLE connection (
                id SERIAL PRIMARY KEY,
                header_id INTEGER,
                timestamp TIMESTAMP,
                version VARCHAR(50),
                manufacturer VARCHAR(100),
                serial_number VARCHAR(100),
                connection_state VARCHAR(50)
            );
        """)
        conn.commit()
        print("Connection table created successfully..")


def create_factsheet_table(conn):
    """Factsheet tablosunu oluşturma fonksiyonu."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'factsheet'
        );
    """)
    if not cursor.fetchone()[0]:
        cursor.execute("""
            CREATE TABLE factsheet (
                id SERIAL PRIMARY KEY,
                header_id INTEGER,
                timestamp TIMESTAMP,
                version VARCHAR(50),
                manufacturer VARCHAR(100),
                serial_number VARCHAR(100),
                series_name VARCHAR(100),
                agv_kinematic VARCHAR(50),
                agv_class VARCHAR(50),
                max_load_mass INTEGER,
                localization_types TEXT[],
                navigation_types TEXT[],
                speed_min REAL,
                speed_max REAL,
                acceleration_max REAL,
                deceleration_max REAL,
                height_min REAL,
                height_max REAL,
                width REAL,
                length REAL,
                -- Protocol Limits
                msg_len INTEGER,
                topic_serial_len INTEGER,
                topic_elem_len INTEGER,
                id_len INTEGER,
                id_numerical_only BOOLEAN,
                enum_len INTEGER,
                load_id_len INTEGER,
                order_nodes_max INTEGER,
                order_edges_max INTEGER,
                node_actions_max INTEGER,
                edge_actions_max INTEGER,
                actions_parameters_max INTEGER,
                instant_actions_max INTEGER,
                trajectory_knot_vector_max INTEGER,
                trajectory_control_points_max INTEGER,
                state_node_states_max INTEGER,
                state_edge_states_max INTEGER,
                state_loads_max INTEGER,
                state_action_states_max INTEGER,
                state_errors_max INTEGER,
                state_information_max INTEGER,
                error_references_max INTEGER,
                information_references_max INTEGER,
                min_order_interval REAL,
                min_state_interval REAL,
                default_state_interval REAL,
                visualization_interval REAL,
                -- Protocol Features
                optional_parameters JSONB,
                agv_actions JSONB, 
                -- AGV Geometry
                wheel_definitions JSONB,
                envelopes_2d JSONB, 
                -- Load Specification
                load_positions TEXT[],
                load_sets JSONB 
            );
        """)
        conn.commit()
        print("Factsheet table created successfully..")

def create_instant_actions_table(conn):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'instant_actions'
        );
    """)
    if not cursor.fetchone()[0]:
        cursor.execute("""
            CREATE TABLE instant_actions (
                id SERIAL PRIMARY KEY,
                header_id INTEGER,
                timestamp TIMESTAMP,
                version VARCHAR(50),
                manufacturer VARCHAR(100),
                serial_number VARCHAR(100),
                actions JSONB 
            );
        """)
        conn.commit()
        print("Instant actions table created successfully..")

def create_order_table(conn):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'orders'
        );
    """)
    if not cursor.fetchone()[0]:
        cursor.execute("""
            CREATE TABLE orders (
                id SERIAL PRIMARY KEY,
                header_id INTEGER,
                timestamp TIMESTAMP,
                version VARCHAR(50),
                manufacturer VARCHAR(100),
                serial_number VARCHAR(100),
                order_id VARCHAR(100),
                order_update_id INTEGER,
                zone_set_id VARCHAR(100),
                nodes JSONB,
                edges JSONB
            );
        """)
        conn.commit()
        print("Order table created successfully..")

def create_state_table(conn):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'state'
        );
    """)
    if not cursor.fetchone()[0]:
        cursor.execute("""
            CREATE TABLE state (
                id SERIAL PRIMARY KEY,
                header_id INTEGER,
                timestamp TIMESTAMP,
                version VARCHAR(50),
                manufacturer VARCHAR(100),
                serial_number VARCHAR(100),
                order_id VARCHAR(100),
                order_update_id INTEGER,
                zone_set_id VARCHAR(100),
                last_node_id VARCHAR(100),
                last_node_sequence_id INTEGER,
                driving BOOLEAN,
                paused BOOLEAN,
                new_base_request BOOLEAN,
                distance_since_last_node REAL,
                operating_mode VARCHAR(50),
                node_states JSONB,
                edge_states JSONB,
                agv_position JSONB,
                velocity JSONB,
                loads JSONB,
                action_states JSONB,
                battery_state JSONB,
                errors JSONB,
                information JSONB,
                safety_state JSONB
            );
        """)
        conn.commit()
        print("State table created successfully.")

