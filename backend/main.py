from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Domain Modules
from graph import generate_synthetic_data, build_graph
from rag import find_best_path, generate_theory, analyze_image_content

app = FastAPI(title="Tinfoil Hat Search Engine", description="The Truth Is Out There")

# Config CORS to allow React Frontend to talk to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, lock this down
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Graph Store
# In a real app, this would be Neo4j or a Persistent Store
GLOBAL_GRAPH = None

class QueryRequest(BaseModel):
    query: str
    model: str = "llama3.2" # Default to llama3.2 since user has it installed

@app.on_event("startup")
def startup_event():
    """Build the Conspiracy Graph on server boot."""
    global GLOBAL_GRAPH
    print("BOOTING: Initializing Conspiracy Logic...")
    texts = generate_synthetic_data()
    GLOBAL_GRAPH = build_graph(texts)
    print(f"ONLINE: Loaded {GLOBAL_GRAPH.number_of_nodes()} truth-nodes.")

@app.get("/graph_data")
def get_graph_data():
    """
    Returns the graph in a format friendly for react-force-graph-3d.
    Format: { "nodes": [{id: "x", group: 1}], "links": [{source: "x", target: "y"}] }
    """
    if not GLOBAL_GRAPH:
        return {"nodes": [], "links": []}
    
    nodes = []
    for n, attr in GLOBAL_GRAPH.nodes(data=True):
        # Color group based on type
        group = 1 if attr.get("type") == "conspiracy" else 2
        nodes.append({"id": n, "group": group, "val": 2 if group==1 else 1})
        
    links = []
    for u, v in GLOBAL_GRAPH.edges():
        links.append({"source": u, "target": v})
        
    return {"nodes": nodes, "links": links}

@app.post("/query")
def run_query(request: QueryRequest):
    """
    Orchestrates Graph RAG + LLM Generation.
    """
    if not GLOBAL_GRAPH:
        raise HTTPException(status_code=503, detail="System not initialized")
        
    path, error_msg = find_best_path(GLOBAL_GRAPH, request.query)
    
    if not path:
        return {
            "found": False,
            "explanation": error_msg,
            "path": []
        }
        
    # We found a path! Generate the madness.
    theory = generate_theory(path, model_name=request.model)
    
    return {
        "found": True,
        "explanation": theory,
        "path": path # Frontend will use this to highlight the route
    }

@app.post("/analyze_image")
async def analyze_image(file: UploadFile = File(...)):
    """
    Receives an image, uses LLaVA to see it, and returns a description.
    """
    try:
        contents = await file.read()
        description = analyze_image_content(contents)
        return {"description": description}
    except Exception as e:
        print(f"ERROR processing image: {str(e)}") # DEBUG
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Run loop for local testing if executed directly
    uvicorn.run(app, host="0.0.0.0", port=8000)
