import networkx as nx
import random
import re

def generate_synthetic_data():
    """
    The Brain's Imagination.
    Generates 20 absurd paragraphs connecting mundane objects to conspiracies.
    """
    mundane_objects = ["Toaster", "Pigeon", "Printer", "Coffee", "5G Tower", "Stop Sign", "Cloud", "Socks", "Microwave", "Cat"]
    connectors = [
        "is actually a receiver for",
        "transmits brainwaves to",
        "was built by",
        "harvests energy from",
        "is a hologram projection of",
        "contains micro-chips tracking",
        "is powered by soul energy from"
    ]
    conspiracies = [
        "The Illuminati", "Bigfoot", "The Moon Landing Set", "Ancient Aliens", "The Deep State", "Lizard People", "The Matrix", "Time Travelers"
    ]
    
    data = []
    
    # Generate direct connections
    for _ in range(15):
        s = random.choice(mundane_objects)
        p = random.choice(connectors)
        o = random.choice(conspiracies)
        text = f"{s} {p} {o}."
        data.append(text)
        
    # Generate multi-hop nonsense (Mundane -> Intermediate -> Conspiracy)
    intermediates = ["Fluoride", "Chemtrails", "Bitcoin", "Oxygen", "Plastic"]
    
    for _ in range(10):
        s = random.choice(mundane_objects)
        i = random.choice(intermediates)
        o = random.choice(conspiracies)
        
        # Sentence 1: Mundane -> Intermediate
        data.append(f"{s} is made of {i}.")
        # Sentence 2: Intermediate -> Conspiracy
        data.append(f"{i} is a byproduct of {o}.")
        
    return data

def build_graph(text_data):
    """
    The Brain's Memory.
    Parses the text and builds a NetworkX Knowledge Graph.
    Subject -> Predicate -> Object
    """
    G = nx.DiGraph()
    
    # Regex-based extraction of "Subject verb/connector Object" patterns
    
    for sentence in text_data:
        sentence = sentence.strip().replace(".", "")
        found = False
        known_connectors = [
            " is actually a receiver for ", " transmits brainwaves to ", " was built by ", 
            " harvests energy from ", " is a hologram projection of ", " contains micro-chips tracking ", 
            " is powered by soul energy from ", " is made of ", " is a byproduct of "
        ]
        
        for conn in known_connectors:
            if conn in sentence:
                parts = sentence.split(conn)
                if len(parts) == 2:
                    subj = parts[0].strip()
                    obj = parts[1].strip()
                    pred = conn.strip()
                    
                    G.add_node(subj, type="mundane" if "Toaster" in str(sentence) else "unknown") # Simplified typing
                    G.add_node(obj, type="conspiracy")
                    G.add_edge(subj, obj, relation=pred)
                    found = True
                    break
        
        if not found:
            # Fallback for manual or diverse sentences
            pass
            
    return G

if __name__ == "__main__":
    # Test it
    texts = generate_synthetic_data()
    G = build_graph(texts)
    print(f"Generated {len(texts)} facts.")
    print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    print("Example Nodes:", list(G.nodes())[:5])
