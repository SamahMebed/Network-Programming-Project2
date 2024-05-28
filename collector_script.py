import sys
import json
import influxdb

from pysnmp.hlapi import *

# InfluxDB client initialization
INFLUXDB_HOST = 'localhost'
INFLUXDB_PORT = 8086
INFLUXDB_DATABASE = 'tempmon_data'
influx_client = influxdb.InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, database=INFLUXDB_DATABASE)


def get_temperature_from_file(switch_id):
    """
    Retrieve temperature data from an SNMP record file.
    """
    file_path = f"/home/samah/Desktop/projectTwo/{switch_id}.snmprec"
    temperatures = []

    try:
        with open(file_path, 'r') as file:
            for line in file:
                oid, temperature = line.strip().split('|')[:2]  # Extract OID and temperature
                temperatures.append(float(temperature))
        return temperatures
    except FileNotFoundError:
        print(f"Error: SNMP record file not found for switch ID {switch_id}")
    except ValueError as e:
        print(f"Error: Invalid SNMP record format - {e}")
    except Exception as e:
        print(f"Error reading SNMP record file: {e}")

    return None


def process_task(task):
    """
    Process task data and write temperature data to InfluxDB.
    """
    switch_id = task.get('switch_id')
    ip_address = task.get('ip_address')

    if not switch_id:
        print("Error: 'switch_id' not found in task data")
        return

    temperatures = get_temperature_from_file(switch_id)
    if temperatures:
        json_body = [
            {
                "measurement": "temperature",
                "tags": {
                    "switch_id": switch_id
                },
                "fields": {
                    "value": temperature
                }
            }
            for temperature in temperatures
        ]

        try:
            influx_client.write_points(json_body)
            print(f"Temperature data for switch ID {switch_id} written to InfluxDB")
        except Exception as e:
            print(f"Error writing temperature data to InfluxDB: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <task_json>")
        sys.exit(1)

    task_json = sys.argv[1]
    try:
        task = json.loads(task_json)
    except json.JSONDecodeError as e:
        print(f"Error parsing task JSON: {e}")
        sys.exit(1)

    process_task(task)
