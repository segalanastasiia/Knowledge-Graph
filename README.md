# Knowledge-Graph
This repository is created for the Storing Data in a Knowledge Graph project in the Designing Technology module at FAU.
## Project overview

The project has the following two main deliverables: 

***1. Knowledge Graph***

***2. Data Scheme***

# Knowledge Graph Schema for Maintenance System

This document contains the initial implementation of a Knowledge Graph schema designed to streamline industrial maintenance workflows. It includes entities, relationships, and Cypher scripts to create and populate the graph in Neo4j, as followed by the first proposed data scheme.

---

## **Schema Overview** (Revision)

### **Entities:**
1. **Equipment**: Machinery or devices used in production.
2. **Part**: Components of equipment that may need maintenance or replacement.
3. **Maintenance Task**: Scheduled or completed tasks for upkeep.
4. **Issue**: Problems or malfunctions with equipment.
5. **Resolution**: Actions taken to resolve issues.
6. **Worker**: Maintenance staff or operators responsible for tasks and reporting issues.
7. **Multimedia**: Multimedia content (Text, Image, Video) that documents maintenance activities, issues, or resolutions.

### **Relationships:**
1. **PERFORMS_TASK**: Worker → Maintenance Task  
2. **AFFECTS**: Issue → Equipment  
3. **RESOLVED_BY**: Issue → Resolution  
4. **HAS_TEXT / HAS_IMAGE / HAS_VIDEO**: Maintenance Task, Issue, or Resolution → Multimedia  
5. **REPORTS_ISSUE**: Worker → Issue  

---

## **Folder Structure**

- `cypher-scripts/`
  - `create_schema.txt`: Defines nodes and relationships.
  - `insert_data.txt`: Inserts sample data.
  - `create_relationships.txt`: Creates relationships between nodes.

---


