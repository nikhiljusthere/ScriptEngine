## =========================== [One Time Installation] ===========================##

1. Install Node (26.0.0)
- winget install OpenJS.NodeJS.LTS

2. Install Electron/ui dependencies:
- npm install
- cd ui
- npm install
- cd ..

3.  Docker
- winget install -e --id Docker.DockerDesktop

4. Install Python dependencies:
- cd python
- powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
- uv python install 3.12
- uv venv --python 3.12
- .venv\Scripts\Activate.ps1
- uv pip install -r requirements.txt 




##  ===========================  [Daily Commands] =========================== ##
0. Run Local Frontend (UI) Server
- npm run dev

1. Crawler
- Run Crawler from ui

2. Build Neo4j Graph
- docker desktop start
- docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
- docker run -p 6333:6333 qdrant/qdrant
Check in docker app and start container manually if not started
- cd python
- python -m pipeline.step2_build_graph

3. Export entities from Neo4j to `entities.json`
-  cypher-shell -u neo4j -p password "MATCH (e:Entity) RETURN e.name" --format plain > raw.txt
OR
in Neo4j browser (http://localhost:7474) run:
- MATCH (e:Entity) RETURN collect(e.name) AS names
Save the result as entities.json

4. Chunk and embed all files
- python step2_chunk_and_embed.py

5. Test retrieval
- python step3_retrieval.py

6. Run full QA 
- python step4_generation.py