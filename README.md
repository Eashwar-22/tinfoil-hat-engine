# Tinfoil Hat Search Engine

A local GraphRAG (Graph Retrieval-Augmented Generation) application that generates connections between mundane objects and conspiracy theories using knowledge graphs and large language models.

## Overview

This project demonstrates a full-stack ML application architecture:
1.  **Knowledge Graph**: Constructs a directed graph of entities using NetworkX.
2.  **Pathfinding**: Algorithms traverse the graph to find connections between user inputs (e.g., "Toaster") and target nodes (e.g., "The Matrix").
3.  **Local RAG**: Uses a local LLM (Llama 3.2 via Ollama) to generate narrative explanations based on the retrieved graph path.
4.  **Computer Vision**: Uses a multimodal model (LLaVA) to analyze uploaded images and integrate visual data into the search pipeline.

## Tech Stack

### Backend
-   **Python**: FastAPI framework.
-   **LangChain**: Orchestrator for LLM interactions.
-   **NetworkX**: Graph data structure and algorithms.
-   **Ollama**: Local inference engine for Llama 3.2 (Text) and LLaVA (Vision).

### Frontend
-   **React**: UI framework used with Vite.
-   **Three.js / React Force Graph**: 3D visualization of the knowledge graph.

## Prerequisites

-   **Ollama**: Must be installed and running.
-   **Python 3.9+**
-   **Node.js & npm**

## Installation & Usage

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/tinfoil-hat-engine.git
    cd tinfoil-hat-engine
    ```

2.  **Run the application**
    The project includes a helper script to manage dependencies and start both servers.
    ```bash
    ./run.sh
    ```

    This script will:
    -   Check if Ollama is running.
    -   Automatically pull required models (`llama3.2` and `llava`) if missing.
    -   Start the FastAPI backend on `http://localhost:8000`.
    -   Start the React frontend on `http://localhost:5173`.

## Architecture Details

-   **backend/graph.py**: Handles synthetic data generation and graph topology construction.
-   **backend/rag.py**: Contains the logic for pathfinding, fuzzy keyword matching, and LLM prompting.
-   **backend/main.py**: FastAPI entry point defining API endpoints (`/query`, `/analyze_image`, `/graph_data`).
-   **frontend/**: Standard React application structure.
