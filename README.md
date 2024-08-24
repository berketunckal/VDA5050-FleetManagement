# Fleet Management

This project implements a fleet management system using MQTT communication for managing automated guided vehicles (AGVs) based on the VDA 5050 protocol. The system includes handling connections, factsheets, orders, instant actions, and state management between the fleet management controller and the AGVs.

## Project Structure

The project is organized into the following directories:

- **fleet_management**: Contains the main scripts for the fleet management functionalities.
- **schemas**: JSON schema files for validating various message types (e.g., `connection.schema`, `factsheet.schema`, etc.).
- **resources**: Configuration files and other resources.
- **tests**: Unit tests for validating the functionalities.

## Features

1. **Connection Handling**: Manages connection states between the fleet manager and the AGVs. It handles MQTT topics related to connection status and publishes/monitors connection states.
  
2. **Factsheet Management**: Publishes and monitors AGV factsheets, which provide detailed specifications and capabilities of the AGVs.

3. **Order Management**: Creates and publishes orders that define the nodes, edges, and actions for the AGVs to follow during task execution.

4. **Instant Actions**: Publishes instant actions that can be executed immediately by AGVs, such as emergency stops, pickups, or drops.

5. **State Management**: Tracks the AGV’s state, including node and edge progress, driving status, battery state, and error handling.

6. **Visualization**: Subscribes to visualization data from AGVs for tracking real-time positions and velocities.

## Getting Started

### Prerequisites

- **Python 3.8+**
- **paho-mqtt**: For MQTT communication.
- **jsonschema**: For JSON schema validation.
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
    keep_alive: 60
    
    fleet_info:
    fleetname: "uagv"
    version: "2.0.0"
    versions: "v2"
    manufacturer: "robots"
    ```

4. Ensure that the JSON schemas are correctly defined under the `schemas/` directory.

### Running the Fleet Manager

To start the fleet management system:

```bash
python3 fleet_manager.py
