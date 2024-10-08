# Fleet Management

This project implements a fleet management system using MQTT communication for managing automated guided vehicles (AGVs) based on the VDA 5050 protocol. The system includes handling connections, factsheets, orders, instant actions, and state management between the fleet management controller and the AGVs.

## Project Structure

The project is organized into the following directories:

- **fleet_management**: Contains the main scripts for the fleet management functionalities.
- **schemas**: JSON schema files for validating various message types (e.g., `connection.schema`, `factsheet.schema`, etc.).
- **resources**: Configuration files and other resources.
- **tests**: Unit tests for validating the functionalities.

## Features

1. **Connection Handling**: 
    - Manages connection states between the fleet manager and the AGVs.
    - Handles MQTT topics related to connection status and publishes/monitors connection states.
    - Implements the use of MQTT's Last Will and Testament (LWT) to notify disconnections.
    - Inserts validated connection data into a PostgreSQL database.

2. **Factsheet Management**: 
    - Publishes and monitors AGV factsheets, which provide detailed specifications and capabilities of the AGVs.
    - Validates incoming factsheets against predefined JSON schemas.
    - Inserts validated factsheet data into a PostgreSQL database.

3. **Order Management**: 
    - Creates and publishes orders that define the nodes, edges, and actions for the AGVs to follow during task execution.
    - Ensures proper sequencing and execution of orders.
    - Inserts order data into a PostgreSQL database.


4. **Instant Actions**: 
    - Publishes instant actions that can be executed immediately by AGVs, such as emergency stops, pickups, or drops.
    - Subscribes to and processes instant action messages, updating the AGV state accordingly.
    - Inserts validated instant actions data into a PostgreSQL database.

5. **State Management**: 
    - Tracks the AGV’s state, including node and edge progress, driving status, battery state, and error handling.
    - Publishes state information to the fleet manager and stores it in the database.
    - Inserts validated state data into a PostgreSQL database.

6. **Visualization**: 
    - Subscribes to visualization data from AGVs for tracking real-time positions and velocities.
    - Updates visual tracking systems with the AGV's current state and position.

## Getting Started

### Prerequisites

- **Python 3.8+**
- **paho-mqtt**: For MQTT communication.
- **jsonschema**: For JSON schema validation.
- **psycopg2**: For PostgreSQL database connection.
- **yaml**: For loading configuration files.

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/berketunckal/VDA5050-FleetManagement.git
    cd fleet_management
    ```

2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up your configuration in `config/config.yaml`. Example configuration:

    ```yaml
    mqtt:
      broker_address: "localhost"
      broker_port: 1883
      keep_alive: 15
    
    fleet_info:
      fleetname: "uagv"
      version: "2.0.0"
      versions: "v2"
      manufacturer: "robots"

    postgres:
      host: "localhost"
      port: 5432
      database: "fleet_db"
      user: "postgres"
      password: "passwd"
    ```

4. Ensure that the JSON schemas are correctly defined under the `schemas/` directory.

5. Create the necessary tables in your PostgreSQL database by running the database setup script:

    ```bash
    python3 setup_database.py
    ```

### Running the Fleet Manager

To start the fleet management system:

```bash
python3 fleet_manager.py
