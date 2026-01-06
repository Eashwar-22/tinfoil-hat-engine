import { useState, useEffect, useRef, useMemo } from 'react'
import ForceGraph3D from 'react-force-graph-3d'
import axios from 'axios'
import './App.css'
import './MissionModal.css'

// Configuration
const API_URL = "http://localhost:8000";

function App() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [query, setQuery] = useState("");
  const [theory, setTheory] = useState(null);
  const [loading, setLoading] = useState(false);
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [highlightLinks, setHighlightLinks] = useState(new Set());
  const [showHelp, setShowHelp] = useState(true); // Default to showing help on load

  const fgRef = useRef();

  // Load Graph Data on Mount
  useEffect(() => {
    axios.get(`${API_URL}/graph_data`)
      .then(res => {
        setGraphData(res.data);
      })
      .then(res => {
        setGraphData(res.data);
      })
      .catch(err => {
        console.error("Failed to connect to Brain:", err);
        setTheory("⚠ SYSTEM OFFLINE: BACKEND IS LOADING OR INSTALLING UPDATES...");
      });
  }, []);

  // Suggestions
  const suggestions = useMemo(() => {
    if (!graphData.nodes.length) return [];
    // Filter for group 2 (mundane)
    const available = graphData.nodes.filter(n => n.group === 2);
    // Shuffle and pick 4
    return available.sort(() => 0.5 - Math.random()).slice(0, 4);
  }, [graphData]);

  const handleSuggestionClick = (val) => {
    setQuery(val);
    // Small timeout to allow state update before search (or just pass val directly)
    // Actually passing directly is cleaner
    search(val);
  };

  // Extracted search function to be reusable
  const search = async (q) => {
    if (!q) return;
    setLoading(true);
    setTheory(null);
    setHighlightNodes(new Set());
    setHighlightLinks(new Set());

    try {
      const res = await axios.post(`${API_URL}/query`, { query: q });

      if (res.data.found) {
        // Update Visualization to highlight path
        const path = res.data.path;
        const nodeSet = new Set(path);
        const linkSet = new Set();

        for (let i = 0; i < path.length - 1; i++) {
          const sourceId = path[i];
          const targetId = path[i + 1];
          linkSet.add(`${sourceId}>${targetId}`);
          linkSet.add(`${targetId}>${sourceId}`);
        }

        setHighlightNodes(nodeSet);
        setHighlightLinks(linkSet);
        setTheory(res.data.explanation);

        if (fgRef.current) {
          const startNode = graphData.nodes.find(n => n.id === path[0]);
          if (startNode) {
            fgRef.current.cameraPosition(
              { x: startNode.x, y: startNode.y, z: startNode.z + 100 },
              startNode,
              3000
            );
          }
        }
      } else {
        setTheory(res.data.explanation);
      }

    } catch (err) {
      setTheory("ERROR: Connection to The Truth Network failed.");
      console.error(err);
    }
    setLoading(false);
  };

  // Node Color Accessor
  const getNodeColor = node => {
    if (highlightNodes.has(node.id)) return "#ff00ff"; // Magenta for path
    return node.group === 1 ? "#ff2222" : "#00ff00";   // Red for Conspiracy, Green for Mundane
  };

  // Link Color Accessor
  const getLinkColor = link => {
    const id1 = `${link.source.id}>${link.target.id}`;
    const id2 = `${link.target.id}>${link.source.id}`;
    if (highlightLinks.has(id1) || highlightLinks.has(id2)) return "#ff00ff";
    return "rgba(0,255,0,0.2)";
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setTheory("ANALYZING VISUAL DATA...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      // 1. Get Description from Vision Model
      const res = await axios.post(`${API_URL}/analyze_image`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      const description = res.data.description;
      setTheory(`DETECTED: ${description} \n\n CROSS-REFERENCING WITH CONSPIRACY DATABASE...`);

      // 2. Search graph with the description
      // We extract the first noun or just search the whole description? 
      // Let's just search the whole description and rely on RAG to make sense of it
      // actually, let's search for "Unknown" to trigger a path, or just use the description as the query

      // Wait a moment for effect
      setTimeout(() => {
        setQuery(description); // Show what was found
        search(description);
      }, 1500);

    } catch (err) {
      console.error(err);
      setTheory("ERROR: IMAGE ANALYSIS FAILED.");
      setLoading(false);
    }
  };

  const fileInputRef = useRef(null);

  return (
    <div className="app-container">

      {/* 3D Graph Background */}
      <div className="graph-wrapper">
        <ForceGraph3D
          ref={fgRef}
          graphData={graphData}
          nodeLabel="id"
          nodeColor={getNodeColor}
          linkColor={getLinkColor}
          linkWidth={link => (highlightLinks.has(`${link.source.id}>${link.target.id}`) || highlightLinks.has(`${link.target.id}>${link.source.id}`)) ? 3 : 1}
          linkOpacity={0.5}
          backgroundColor="#000000"
          nodeRelSize={6}
        />
      </div>

      {/* HUD UI */}
      <div className="hud-container">

        <div className="top-bar">
          <div className="title">Tinfoil Hat Search Engine v1.0</div>
          <div className="status">STATUS: {loading ? "DECRYPTING..." : "CONNECTED"}</div>
        </div>

        {/* Search Overlay */}
        <div className="search-box-container">
          <div>
            <input
              type="text"
              className="search-input"
              placeholder="Enter Subject (e.g. Toaster)"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && search(query)}
            />
            <button className="search-btn" onClick={() => search(query)}>EXPOSE</button>

            {/* EVIDENCE UPLOAD */}
            <input
              type="file"
              accept="image/*"
              ref={fileInputRef}
              style={{ display: 'none' }}
              onChange={handleFileUpload}
            />
            <button
              className="search-btn evidence-btn"
              onClick={() => fileInputRef.current.click()}
              title="Upload Photo for Analysis"
            >
              📷 EVIDENCE
            </button>
          </div>

          {/* Suggestions Chips */}
          {!theory && suggestions.length > 0 && (
            <div className="suggestions-container">
              <div style={{ width: '100%', fontSize: '0.8rem', opacity: 0.7 }}>DETECTED SIGNALS:</div>
              {suggestions.map(node => (
                <div key={node.id} className="suggestion-chip" onClick={() => handleSuggestionClick(node.id)}>
                  {node.id}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Results Panel */}
        {theory && (
          <div className="result-panel">
            <h3>TRUTH EXPOSED:</h3>
            <p className="typing-cursor">{theory}</p>
          </div>
        )}

        <div className="status-bar">
          NODES: {graphData.nodes.length} | LINKS: {graphData.links.length} | OLLAMA: ACTIVE
        </div>

      </div>

      {/* Mission Briefing Modal */}
      {showHelp && (
        <div className="modal-overlay">
          <div className="mission-briefing">
            <h1>CLASSIFIED BRIEFING</h1>
            <p>
              Welcome, Agent. This system reveals the <span className="key-term">Hidden Connections</span> between mundane objects and global conspiracies.
            </p>
            <p>
              <strong>How it works:</strong><br />
              1. Our AI analyzes the "Knowledge Graph" (the floating web behind you).<br />
              2. Search for a harmless word like <span className="key-term">"Toaster"</span>.<br />
              3. We trace the path from your object to <span className="key-term">The Truth</span>.
            </p>
            <button className="enter-btn" onClick={() => setShowHelp(false)}>ENTER SYSTEM</button>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
