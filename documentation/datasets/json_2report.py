import os
import json
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from neo4j import GraphDatabase
from fpdf import FPDF

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"  # Replace with your actual password

# Initialize Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def create_nodes_from_json(file_path: str, label: str) -> None:
    """Create nodes in Neo4j from a JSON file."""
    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        with driver.session() as session:
            for record in data:
                query = f"CREATE (n:{label} {{"
                query += ', '.join([f"{key}: ${key}" for key in record.keys()])
                query += "})"
                session.run(query, **record)
    except Exception as e:
        print("Error during node creation:", e)


def create_edges_from_json(file_path: str, node_label: str, edge_label: str) -> None:
    """Create edges in Neo4j from a JSON file."""
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


def fetch_data_from_neo4j(node_label: str):
    """Retrieve data from Neo4j to be used in the PDF report."""
    try:
        with driver.session() as session:
            query = f"MATCH (n:{node_label}) RETURN n"
            result = session.run(query)
            nodes = [record["n"] for record in result]
        return nodes
    except Exception as e:
        print("Error fetching data from Neo4j:", e)
        return []


def generate_pdf_report(node_label: str, output_path="neo4j_report.pdf"):
    """Generate a PDF report from Neo4j data."""
    try:
        data = fetch_data_from_neo4j(node_label)
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "Neo4j Knowledge Graph Report", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", size=12)
        for node in data:
            pdf.cell(0, 10, f"Node ID: {node.id}", ln=True)
            for key, value in node.items():
                pdf.multi_cell(0, 10, f"{key}: {value}")
            pdf.ln(5)

        pdf.output(output_path)
        print(f"PDF report generated: {output_path}")
    except Exception as e:
        print("Error generating PDF report:", e)


def process_data_pipeline(**context):
    """Task to orchestrate data writing for nodes, edges, and generating a PDF report."""
    dataset = "example_dataset"
    node_label = "Equipment"
    edge_label = "CONNECTED_TO"

    # Define file paths
    node_file_path = os.path.join("datasets", f"{dataset}_nodes.json")
    edge_file_path = os.path.join("datasets", f"{dataset}_edges.json")

    # Write data to Neo4j
    create_nodes_from_json(node_file_path, node_label)
    create_edges_from_json(edge_file_path, node_label, edge_label)

    # Generate PDF report from Neo4j data
    generate_pdf_report(node_label, "airflow_generated_report.pdf")


# Define Airflow DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="neo4j_json_to_pdf_pipeline",
    default_args=default_args,
    description="Pipeline to upload JSON to Neo4j and generate a PDF report",
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:

    process_task = PythonOperator(
        task_id="process_neo4j_data",
        python_callable=process_data_pipeline,
        provide_context=True,
    )

    process_task

# Close the driver after the DAG completes
def close_driver():
    if driver:
        driver.close()

close_driver()
