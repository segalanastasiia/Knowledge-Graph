## **Quick Start**

### **1. Prerequisites**
- Install [Neo4j Desktop](https://neo4j.com/download/) or run a Neo4j instance.
- Create database and password to analyse and view the data
- Start the database
- Clone this repository on your local machine to access the example data (optional)

### **2. Run scripts in Neo4j interface**
## Create schema 
```cypher
from "cypher-scripts/create_schema.cypher" 
```
## Insert sample data
```cypher
from "cypher-scripts/insert_data.cypher"
```
## Create relationships 
```cypher
from "cypher-scripts/create_relationships.cypher"
```
## Visualize schema
```cypher
CALL db.schema.visualization();
```