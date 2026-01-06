import networkx as nx
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
import os
import base64
import io

from PIL import Image

def find_best_path(G, start_node):
    """
    The 'Retrieval' step.
    Travels the graph to find the shortest path from the mundane input to a Conspiracy.
    """
    # 1. Identify potential targets
    targets = [n for n, attr in G.nodes(data=True) if attr.get("type") == "conspiracy"]
    
    if not targets:
        return None, "No conspiracies found in the database. System Error."

    # 2. Key Step: Normalize Input Logic
    start_node = start_node.strip()
    detected_node = None
    
    # Direct match first (case-insensitive)
    for n in G.nodes():
        if n.lower() == start_node.lower():
            detected_node = n
            break
            
    # Fuzzy match second (substring search)
    if not detected_node:
        # Sort nodes by length descending so we match "5G Tower" before "Tower"
        sorted_nodes = sorted(list(G.nodes()), key=len, reverse=True)
        for n in sorted_nodes:
            # If the node name (e.g. "Toaster") appears in the user query (e.g. "My Toaster is broken")
            if n.lower() in start_node.lower():
                detected_node = n
                break
                
    if not detected_node:
        return None, f"'{start_node}' is not in the system. The government wiped it."

    # 3. Pathfinding
    shortest_path = None
    min_length = float('inf')
    
    for target in targets:
        try:
            path = nx.shortest_path(G, source=detected_node, target=target)
            if len(path) < min_length:
                min_length = len(path)
                shortest_path = path
        except nx.NetworkXNoPath:
            continue
            
    if not shortest_path:
        return None, "You are safe... for now. No connection found."
        
    return shortest_path, None

def generate_theory(path, model_name="llama3.2"):
    """
    The 'Generation' step using Ollama (Local LLM).
    Turns a list of nodes ["Toaster", "Receiver", "Illuminati"] into a story.
    """
    path_str = " -> ".join(path)
    
    llm = ChatOllama(
        model=model_name,
        temperature=0.9,
    )
    
    template = """
    You are a paranoid conspiracy theorist. 
    I will give you a chain of connections found in our knowledge graph.
    You must explain how the start causes the end.
    
    The Chain: {path}
    
    Rules:
    1. Be concise but intense.
    2. Use the exact nodes in the chain.
    3. SOUND CRAZY.
    4. Do NOT introduce yourself, just scream the theory.
    
    Theory:
    """
    
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    
    try:
        response = chain.invoke({"path": path_str})
        return response.content
    except Exception as e:
        return f"ERROR: Could not connect to Ollama. Is it running? (Error: {str(e)})"

def analyze_image_content(image_bytes, model_name="llava"):
    """
    Uses LLaVA (Vision LLM) to describe what makes the image 'suspicious'.
    """
    llm = ChatOllama(
        model=model_name,
        temperature=0.8,
    )
    
    # Optimize: Resize image to max 512px to speed up local interference
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.thumbnail((512, 512)) # Downscale
        
        # Save back to bytes
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        optimized_bytes = buffered.getvalue()
        
        # encoding image to base64
        image_b64 = base64.b64encode(optimized_bytes).decode('utf-8')
    except Exception as e:
        return f"ERROR: Image processing failed ({str(e)})"
    
    # Prompting LlaVa
    # We ask it to identify the object AND imply it's suspicious
    messages = [
        ("human", [
            {"type": "text", "text": "Identify the main object in this image (e.g. Toaster, Cat, Car). Then, in one short sentence, verify consistent with: 'This looks like a standard [Object], but there is something off about its energy.'"},
            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_b64}"},
        ])
    ]
    
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"ERROR: Vision Module Malfunction. (Error: {str(e)})"
