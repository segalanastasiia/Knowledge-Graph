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
NEO4J_PASSWORD = "password"  # Replace with actual password

# Initialize Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def create_nodes_and_edges_from_json(file_path: str) -> None:
    """Create nodes and edges in Neo4j from a hierarchical JSON file."""
    try:
        with open(file_path, "r") as file:
            data = json.load(file)["data"]

        with driver.session() as session:
            for entry in data:
                # Create Machine node
                machine = entry["Machine"]
                machine_query = f"""
                MERGE (m:Machine {{id: $id}})
                SET m += $properties
                """
                session.run(machine_query, id=machine["id"], properties=machine)

                # Create Part node and relation
                part = entry["Part"]
                part_query = f"""
                MERGE (p:Part {{id: $id}})
                SET p += $properties
                WITH p
                MATCH (m:Machine {{id: $machine_id}})
                MERGE (m)-[:HAS_PART]->(p)
                """
                session.run(part_query, id=part["id"], properties=part, machine_id=part["machine_id"])

                # Create Supervisor node and relation
                supervisor = entry["Supervisor"]
                supervisor_query = f"""
                MERGE (s:Supervisor {{id: $id}})
                SET s += $properties
                """
                session.run(supervisor_query, id=supervisor["id"], properties=supervisor)

                # Create relation between Supervisor and Machine
                for machine_id in supervisor["responsible_machines"]:
                    relation_query = f"""
                    MATCH (s:Supervisor {{id: $supervisor_id}})
                    MATCH (m:Machine {{id: $machine_id}})
                    MERGE (s)-[:OVERSEES]->(m)
                    """
                    session.run(relation_query, supervisor_id=supervisor["id"], machine_id=machine_id)

                # Create Manual node and relation
                manual = entry["Manual"]
                manual_query = f"""
                MERGE (man:Manual {{id: $id}})
                SET man += $properties
                """
                session.run(manual_query, id=manual["id"], properties=manual)

                for machine_id in manual["applies_to"]:
                    relation_query = f"""
                    MATCH (man:Manual {{id: $manual_id}})
                    MATCH (m:Machine {{id: $machine_id}})
                    MERGE (m)-[:HAS_MANUAL]->(man)
                    """
                    session.run(relation_query, manual_id=manual["id"], machine_id=machine_id)

                # Create Worker node and relation
                worker = entry["Worker"]
                worker_query = f"""
                MERGE (w:Worker {{id: $id}})
                SET w += $properties
                WITH w
                MATCH (s:Supervisor {{id: $supervisor_id}})
                MERGE (s)-[:SUPERVISES]->(w)
                """
                session.run(worker_query, id=worker["id"], properties=worker, supervisor_id=worker["supervisor_id"])

        print("JSON data successfully inserted into Neo4j.")
    except Exception as e:
        print("Error inserting JSON data:", e)


def fetch_data_from_neo4j():
    """Retrieve knowledge from Neo4j for report generation."""
    try:
        with driver.session() as session:
            query = """
            MATCH (m:Machine)-[:OVERSEES]-(s:Supervisor)
            OPTIONAL MATCH (m)-[:HAS_PART]->(p:Part)
            OPTIONAL MATCH (m)-[:HAS_MANUAL]->(man:Manual)
            OPTIONAL MATCH (s)-[:SUPERVISES]->(w:Worker)
            RETURN m, s, p, man, w
            """
            result = session.run(query)
            data = []
            for record in result:
                machine = record["m"]
                supervisor = record["s"]
                part = record["p"]
                manual = record["man"]
                worker = record["w"]
                data.append({
                    "machine": machine,
                    "supervisor": supervisor,
                    "part": part,
                    "manual": manual,
                    "worker": worker
                })
        return data
    except Exception as e:
        print("Error fetching data from Neo4j:", e)
        return []


def generate_pdf_report(output_path="neo4j_report.pdf"):
    """Generate a PDF report based on the knowledge graph."""
    try:
        data = fetch_data_from_neo4j()
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "Factory Equipment Report", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", size=12)
        for entry in data:
            machine = entry["machine"]
            supervisor = entry["supervisor"]
            part = entry.get("part")
            manual = entry.get("manual")
            worker = entry.get("worker")

            pdf.cell(0, 10, f"Machine: {machine['name']} (ID: {machine['id']})", ln=True)
            pdf.cell(0, 10, f"Location: {machine['location']}", ln=True)
            pdf.cell(0, 10, f"Status: {machine['status']}", ln=True)
            pdf.cell(0, 10, f"Last Maintenance: {machine['last_maintenance_date']}", ln=True)

            pdf.cell(0, 10, f"Supervisor: {supervisor['name']} (ID: {supervisor['id']})", ln=True)

            if part:
                pdf.cell(0, 10, f"Part: {part['name']} (Material: {part['material']})", ln=True)

            if manual:
                pdf.cell(0, 10, f"Manual: {manual['title']} (URL: {manual['url']})", ln=True)

            if worker:
                pdf.cell(0, 10, f"Worker: {worker['name']} (Role: {worker['role']})", ln=True)

            pdf.ln(10)

        pdf.output(output_path)
        print(f"PDF report generated: {output_path}")
    except Exception as e:
        print("Error generating PDF report:", e)


def run_data_pipeline(**context):
    """Run the entire data pipeline: JSON to Neo4j and PDF generation."""
    json_file_path = "/mnt/data/Nodes.json"

    # Insert data into Neo4j
    create_nodes_and_edges_from_json(json_file_path)

    # Generate PDF Report
    generate_pdf_report("factory_equipment_report.pdf")


# Define Apache Airflow DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="neo4j_factory_pipeline",
    default_args=default_args,
    description="Ingest factory data into Neo4j and generate PDF report",
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:

    process_task = PythonOperator(
        task_id="run_pipeline",
        python_callable=run_data_pipeline,
        provide_context=True,
    )

    process_task

# Close the driver after execution
def close_driver():
    if driver:
        driver.close()

close_driver()
