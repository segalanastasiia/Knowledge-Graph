import os
import json
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from neo4j import GraphDatabase
from fpdf import FPDF

# Neo4j connection details
NEO4J_URI = "neo4j+s://ac96daaf.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "kmJBCczSRM7DXFo2YUJLE2THi0_4QNysoaOc_rwDuV4"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def check_connection():
    try:
        with driver.session() as session:
            session.run("RETURN 1").single()
        print("Connection successful.")
    except Exception as e:
        print("Failed to connect. ", e)

def create_nodes_from_json(file_path: str) -> None:
    """Create nodes in Neo4j from a JSON file."""
    try:
        with open(file_path, "r") as file:
            data = json.load(file)["data"]

        with driver.session() as session:
            for entry in data:
                for node_type, node_data in entry.items():
                    query = f"""
                    MERGE (n:{node_type} {{id: $id}})
                    SET n += $properties
                    """
                    session.run(query, id=node_data["id"], properties=node_data)

        print("Nodes successfully inserted into Neo4j.")
    except Exception as e:
        print("Error inserting nodes:", e)

check_connection()

def create_edges_from_json(file_path: str) -> None:
    """Create edges in Neo4j from an edges JSON file."""
    try:
        with open(file_path, "r") as file:
            edges_data = json.load(file)["edges"]

        with driver.session() as session:
            for edge_group in edges_data:
                source_label = edge_group["source"]
                target_label = edge_group["target"]
                relationship = edge_group["relationship"]
                
                for edge in edge_group["edges"]:
                    query = f"""
                    MATCH (a:{source_label} {{id: $source_id}})
                    MATCH (b:{target_label} {{id: $target_id}})
                    MERGE (a)-[:{relationship}]->(b)
                    """
                    session.run(query, source_id=edge["source_id"], target_id=edge["target_id"])
        print("Edges successfully inserted into Neo4j.")
    except Exception as e:
        print("Error inserting edges:", e)

create_nodes_from_json("/Users/evi/Documents/GitHub/Knowledge-Graph/documentation/SyntheticData/Nodes.json")
create_edges_from_json("/Users/evi/Documents/GitHub/Knowledge-Graph/documentation/SyntheticData/Edges.json")

def fetch_data_from_neo4j():
    """Retrieve data from Neo4j for report generation."""
    try:
        with driver.session() as session:
            query = "MATCH (n) RETURN n"
            result = session.run(query)
            return [record["n"] for record in result]
    except Exception as e:
        print("Error fetching data from Neo4j:", e)
        return []

def generate_pdf_report(output_path="neo4j_report.pdf"):
    """Generate a PDF report from Neo4j data."""
    try:
        data = fetch_data_from_neo4j()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "Factory Equipment Report", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        
        for node in data:
            pdf.cell(0, 10, f"Node: {node['id']} ({node['label']})", ln=True)
            for key, value in node.items():
                if key not in ["id", "label"]:
                    pdf.cell(0, 10, f"  {key}: {value}", ln=True)
            pdf.ln(5)
        
        pdf.output(output_path)
        print(f"PDF report generated: {output_path}")
    except Exception as e:
        print("Error generating PDF report:", e)

# def run_data_pipeline():
#     """Run data ingestion and reporting pipeline."""
#     nodes_file_path = "/mnt/data/Nodes.json"
#     edges_file_path = "/mnt/data/Edges.json"

#     create_nodes_from_json(nodes_file_path)
#     create_edges_from_json(edges_file_path)
#     generate_pdf_report("factory_equipment_report.pdf")

def close_driver():
    if driver:
        driver.close()

# Define Apache Airflow DAG
# default_args = {"owner": "airflow", "depends_on_past": False, "retries": 1}
# with DAG(
#     dag_id="neo4j_factory_pipeline",
#     default_args=default_args,
#     description="Ingest factory data into Neo4j and generate PDF report",
#     schedule_interval=None,
#     start_date=datetime(2025, 1, 1),
#     catchup=False,
# ) as dag:
#     check_connection_task = PythonOperator(
#         task_id="check_neo4j_connection",
#         python_callable = check_connection,
#     )
    
#     load_nodes_task = PythonOperator(
#         task_id="load_nodes",
#         python_callable=create_nodes_from_json,
#         op_kwargs={'nodes_file_path': 'SyntheticData/Nodes.json'},
#     )
    
#     load_edges_task = PythonOperator(
#         task_id="load_edges",
#         python_callable=create_edges_from_json,
#         op_kwargs={'edges_file_path': 'SyntheticData/Edges.json'},
#     )

#     generate_report_task = PythonOperator(
#         task_id="generate_report",
#         python_callable=generate_pdf_report,
#         op_kwargs={'output_path': "factory_equipment_report.pdf"},
#     )

#     check_connection_task >> [load_nodes_task, load_edges_task] >> generate_report_task

close_driver()
