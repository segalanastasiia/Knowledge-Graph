# Knowledge-Graph
This repository is created for the Storing Data in a Knowledge Graph project in the Designing Technology module at FAU.
## Project overview

The project has the following two main deliverables: 

***1. Knowledge Graph***

***2. Data Scheme***

# Knowledge Graph Schema for Maintenance System

This document contains the proposed implementation of a Knowledge Graph schema designed to streamline industrial maintenance workflows. It includes entities, relationships, as well as described folder structre for orientation.

![full_graph](https://github.com/user-attachments/assets/eefb85b2-016a-43db-a196-40cee1258d47)


---

## **Schema Overview**

### **Entities:**
1. `Machine`: Machinery or devices used in production.
2. `Part`: Components that belong to machines and may require maintenance or replacement.
3. `Supervisor`: Oversees workers and assigns tasks.
4. `Worker`: Performs maintenance tasks, reports issues, and applies solutions.
5. `Manual`: Documentation that provides instructions for tasks, machines, and useful for solutions.
6. `Report`: A document detailing an issue, task, or resolution.
7. `Error`: A malfunction, issue, or problem affecting machines or parts.
8. `Task`: A maintenance or repair action assigned to a worker.
9. `Solution`: Actions, tools, and materials used to fix errors.
10. `Multimedia`: Images, videos, audio or text used to document reports, tasks, and solutions.

### **Relationships:**
1. **Machine Relationships**
   - `(:Machine)-[:HAS_PART]->(:Part)` → A machine is composed of parts.
   - `(:Machine)-[:DESCRIBED_IN]->(:Manual)` → A machine is documented in a manual.
   - `(:Machine)-[:MENTIONED_IN]->(:Multimedia)` → A machine appears in multimedia.
   - `(:Machine)-[:TARGETED_BY]->(:Task)` → A task is assigned to a machine.
   - `(:Machine)-[:AFFECTS]->(:Error)` → A machine causes an error.
   - `(:Machine)-[:REPORTED_IN]->(:Report)` → A machine is mentioned in a report.

2. **Part Relationships**
   - `(:Part)-[:USED_IN]->(:Machine)` → A part is used in a machine.
   - `(:Part)-[:SUB_PART_OF]->(:Part)` → A part is a sub-component of another part.
   - `(:Part)-[:AFFECTS]->(:Error)` → A part causes an error.
   - `(:Part)-[:REPORTED_IN]->(:Report)` → A part is mentioned in a report.
   - `(:Part)-[:TARGETED_BY]->(:Task)` → A part is involved in a task.
   - `(:Part)-[:MENTIONED_IN]->(:Multimedia)` → A part appears in multimedia.

3. **Supervisor Relationships**
   - `(:Supervisor)-[:SUPERVISES]->(:Worker)` → A supervisor oversees a worker.
   - `(:Supervisor)-[:ASSIGNS]->(:Task)` → A supervisor assigns a task.
   - `(:Supervisor)-[:ACCEPTS]->(:Report)` → A supervisor accepts a report.
   - `(:Supervisor)-[:CONFIRMS]->(:Solution)` → A supervisor confirms a solution.

4. **Worker Relationships**
   - `(:Worker)-[:SUPERVISED_BY]->(:Supervisor)` → A worker is supervised by a supervisor.
   - `(:Worker)-[:ASSIGNED_TO]->(:Task)` → A worker is assigned a task.
   - `(:Worker)-[:REPORTS]->(:Error)` → A worker reports an error.
   - `(:Worker)-[:COMPILES]->(:Report)` → A worker compiles a report.
   - `(:Worker)-[:APPLIES]->(:Solution)` → A worker applies a solution.

5. **Manual Relationships**
   - `(:Manual)-[:APPLIES_TO]->(:Machine)` → A manual applies to a machine.
   - `(:Manual)-[:COVERS]->(:Task)` → A manual provides documentation for a task.
   - `(:Manual)-[:REFERRED_BY]->(:Report)` → A manual is referenced in a report.

6. **Report Relationships**
   - `(:Report)-[:RELATES_TO]->(:Machine)` → A report relates to a machine.
   - `(:Report)-[:RELATES_TO]->(:Part)` → A report relates to a part.
   - `(:Report)-[:ACCEPTED_BY]->(:Supervisor)` → A report is accepted by a supervisor.
   - `(:Report)-[:COMPILED_BY]->(:Worker)` → A report is compiled by a worker.
   - `(:Report)-[:REFERENCES]->(:Manual)` → A report references a manual.
   - `(:Report)-[:MENTIONS]->(:Error)` → A report mentions an error.
   - `(:Report)-[:CONTAINS]->(:Multimedia)` → A report contains multimedia.

7. **Error Relationships**
   - `(:Error)-[:CAUSED_BY]->(:Machine)` → An error is caused by a machine.
   - `(:Error)-[:CAUSED_BY]->(:Part)` → An error is caused by a part.
   - `(:Error)-[:FIXED_BY]->(:Worker)` → An error is fixed by a worker.
   - `(:Error)-[:SOLVED_BY]->(:Solution)` → An error is solved by a solution.
   - `(:Error)-[:MENTIONED_IN]->(:Report)` → An error is mentioned in a report.
   - `(:Error)-[:CONTAINS]->(:Multimedia)` → An error contains multimedia.

8. **Task Relationships**
   - `(:Task)-[:TARGETS]->(:Machine)` → A task targets a machine.
   - `(:Task)-[:TARGETS]->(:Part)` → A task targets a part.
   - `(:Task)-[:USES_DOCUMENTATION_FROM]->(:Manual)` → A task is covered by a manual.
   - `(:Task)-[:ASSIGNED_TO]->(:Worker)` → A task is assigned to a worker.
   - `(:Task)-[:ASSIGNED_BY]->(:Supervisor)` → A task is assigned by a supervisor.
   - `(:Task)-[:CONTAINS]->(:Multimedia)` → A task contains multimedia.

9. **Solution Relationships**
   - `(:Solution)-[:SOLVES]->(:Error)` → A solution solves an error.
   - `(:Solution)-[:REUSES_SOLUTION_OF]->(:Solution)` → A solution reuses another solution.
   - `(:Solution)-[:USES]->(:Multimedia)` → A solution uses multimedia.
   - `(:Solution)-[:APPLIED_BY]->(:Worker)` → A solution is applied by a worker.
   - `(:Solution)-[:CONFIRMED_BY]->(:Supervisor)` → A solution is confirmed by a supervisor.

10. **Multimedia Relationships**
   - `(:Multimedia)-[:DOCUMENTS]->(:Error)` → Multimedia documents an error.
   - `(:Multimedia)-[:INCLUDED_IN]->(:Report)` → Multimedia is included in a report.
   - `(:Multimedia)-[:INCLUDED_IN]->(:Task)` → Multimedia is included in a task.
   - `(:Multimedia)-[:USED_IN]->(:Solution)` → Multimedia is used in a solution.
   - `(:Multimedia)-[:MENTIONS]->(:Machine)` → Multimedia mentions a machine.
   - `(:Multimedia)-[:MENTIONS]->(:Part)` → Multimedia mentions a part.

---

## **Folder Structure**
- `scripts/`
  - `json_2report.py` - Import bulk initial data to Knowledge Graph.
  - `apache_2json.py` - Import data from ongoing streamline processes.
- `SyntheticData/` - Synthetic .json files generated with the help of ChatGPT to mimic data import. .xlsx file of written data schema.
- `exampleScenarios/` - Images from Neo4j Aura to demonstrate schema of example use case scenarios.
- `archive/` - To store outdated methods.
  - `scripts/`
  - `data/`
  - `ideas`


