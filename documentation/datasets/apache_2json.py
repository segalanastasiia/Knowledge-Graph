import os
import json
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from neo4j import GraphDatabase

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"  # Replace with your Neo4j password

# Initialize Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def create_nodes_from_json(file_path: str, label: str) -> None:
    """
    Create nodes in Neo4j from a JSON file.

    Args:
        file_path (str): Path to the JSON file containing node data.
        label (str): Label for the nodes in Neo4j.
    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        with driver.session() as session:
            for record in data:
                # Create Cypher query with dynamic property mapping
                query = f"CREATE (n:{label} {{"
                query += ', '.join([f"{key}: ${key}" for key in record.keys()])
                query += "})"

                # Execute the query with properties from the record
                session.run(query, **record)
    except Exception as e:
        print("Error during node creation:", e)


def create_edges_from_json(file_path: str, node_label: str, edge_label: str) -> None:
    """
    Create edges in Neo4j from a JSON file.

    Args:
        file_path (str): Path to the JSON file containing edge data.
        node_label (str): Label for the nodes.
        edge_label (str): Label for the edges in Neo4j.
    """
    try:
        with open(file_path, "r") as file:
            edge_data = json.load(file)

        with driver.session() as session:
            for record in edge_data:
                source_id = record['source_id']
                target_id = record['target_id']
                properties = {key: value for key, value in record.items() if key not in ["source_id", "target_id"]}

                query = f"""
                MATCH (source:{node_label} {{id: $source_id}})
                MATCH (target:{node_label} {{id: $target_id}})
                MERGE (source)-[:{edge_label} {{ {', '.join([f'{k}: ${k}' for k in properties])} }}]->(target)
                """
                session.run(query, source_id=source_id, target_id=target_id, **properties)
    except Exception as e:
        print("Error during edge creation:", e)


def write_to_neo4j(**context):
    """
    Task to orchestrate data writing for nodes and edges to Neo4j.
    """
    dataset = "example_dataset"
    node_label = "Equipment"
    edge_label = "CONNECTED_TO"

    # Define file paths
    node_file_path = os.path.join("datasets", f"{dataset}_nodes.json")
    edge_file_path = os.path.join("datasets", f"{dataset}_edges.json")

    # Write data to Neo4j
    create_nodes_from_json(node_file_path, node_label)
    create_edges_from_json(edge_file_path, node_label, edge_label)


# Define Airflow DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="neo4j_dynamic_write_json_dag",
    default_args=default_args,
    description="Dynamic Data Write to Neo4j from JSON",
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:

    write_task = PythonOperator(
        task_id="write_to_neo4j",
        python_callable=write_to_neo4j,
        provide_context=True,
    )

    write_task

# Close the driver after the DAG completes
def close_driver():
    if driver:
        driver.close()

close_driver()

