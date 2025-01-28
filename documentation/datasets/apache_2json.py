import json
from neo4j import GraphDatabase

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_password"

# Initialize Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def create_nodes(file_path: str):
    """Load nodes from a JSON file and create them in Neo4j."""
    try:
        with open(file_path, "r") as file:
            nodes = json.load(file)

        with driver.session() as session:
            for node in nodes:
                label = node.pop("label", "GenericNode")  # Default label if not provided
                properties = {key: value for key, value in node.items()}
                
                query = f"CREATE (n:{label} {{"
                query += ", ".join([f"{key}: ${key}" for key in properties.keys()])
                query += "})"
                
                session.run(query, **properties)
    except Exception as e:
        print("Error creating nodes:", e)


def create_relationships(file_path: str):
    """Load relationships from a JSON file and create them in Neo4j."""
    try:
        with open(file_path, "r") as file:
            relationships = json.load(file)

        with driver.session() as session:
            for rel in relationships:
                source_id = rel["source_id"]
                target_id = rel["target_id"]
                rel_type = rel.get("type", "RELATED_TO")
                
                query = f"""
                MATCH (a {{id: $source_id}})
                MATCH (b {{id: $target_id}})
                MERGE (a)-[:{rel_type}]->(b)
                """
                
                session.run(query, source_id=source_id, target_id=target_id)
    except Exception as e:
        print("Error creating relationships:", e)


# File paths for JSON files
node_file_path = "path_to_nodes.json"
relationship_file_path = "path_to_relationships.json"

# Load and write data to Neo4j
create_nodes(node_file_path)
create_relationships(relationship_file_path)

# Close the driver
driver.close()

