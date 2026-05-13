import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Search, BookOpen, ExternalLink, Sparkles, X, ChevronRight, BarChart3, Share2, MessageSquare, Send, Zap, Info, Target, AlertCircle, Repeat } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Plot from 'react-plotly.js';
import ForceGraph2D from 'react-force-graph-2d';
import './App.css';

// v2.1 - Features: Chat, Insights, ForceGraph
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError(error) { return { hasError: true }; }
  componentDidCatch(error, errorInfo) { console.error("Crash caught:", error, errorInfo); }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '5rem', textAlign: 'center', color: 'white' }}>
          <h2>Oops! Something went wrong in the Library.</h2>
          <p>This is usually caused by a data mismatch. We've logged the error.</p>
          <button onClick={() => { this.setState({ hasError: false }); window.location.reload(); }} style={{ padding: '0.8rem 2rem', background: '#6366f1', border: 'none', borderRadius: '50px', color: 'white', cursor: 'pointer', marginTop: '1.5rem', fontWeight: 'bold' }}>
            Refresh & Fix
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [readingList, setReadingList] = useState([]);
  const [history, setHistory] = useState([]);
  const [view, setView] = useState('search'); // 'search' or 'library'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Detail View State
  const [selectedPaper, setSelectedPaper] = useState(null);
  const [aiSummary, setAiSummary] = useState('');
  const [relatedPapers, setRelatedPapers] = useState([]);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [recsLoading, setRecsLoading] = useState(false);
  const [trends, setTrends] = useState(null);

  // New Features State
  const [insights, setInsights] = useState(null);
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [graphLoading, setGraphLoading] = useState(false);
  
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const fetchReadingList = async () => {
    try {
      const response = await axios.get(`${API_BASE}/reading-list`);
      setReadingList(response.data);
    } catch (err) {
      console.error('Failed to fetch reading list', err);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE}/history`);
      setHistory(response.data);
    } catch (err) {
      console.error('Failed to fetch history', err);
    }
  };

  useEffect(() => {
    fetchReadingList();
    fetchHistory();
  }, []);

  const isSaved = (paperId) => {
    return readingList.some(p => p.paper_id === paperId);
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_BASE}/search`, { 
        query,
        max_results: 10 
      });
      setResults(response.data);
      fetchTrends(query);
      fetchHistory(); 
    } catch (err) {
      setError('Failed to fetch papers. Make sure the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchTrends = async (topic) => {
    try {
      const response = await axios.get(`${API_BASE}/trends/${topic}`);
      setTrends(response.data);
    } catch (err) {
      console.error(err);
    }
  };

  const openDetail = async (paper) => {
    const normalizedPaper = {
      id: paper.id || paper.paper_id,
      title: paper.title,
      authors: Array.isArray(paper.authors) ? paper.authors : (paper.authors?.split(', ') || []),
      abstract: paper.abstract,
      link: paper.link
    };
    
    setSelectedPaper(normalizedPaper);
    setAiSummary('');
    setRelatedPapers([]);
    setInsights(null);
    setChatMessages([
      { role: 'ai', content: `Hello! I've indexed "${normalizedPaper.title}". What would you like to know about it?` }
    ]);
    setGraphData({ nodes: [], links: [] });
    
    setSummaryLoading(true);
    setRecsLoading(true);
    setInsightsLoading(true);
    setGraphLoading(true);
    
    const paperId = normalizedPaper.id;

    // 1. Summary
    axios.post(`${API_BASE}/summarize`, { text: normalizedPaper.abstract })
      .then(res => setAiSummary(res.data.summary))
      .catch(() => setAiSummary("Failed to generate AI summary."))
      .finally(() => setSummaryLoading(false));

    // 2. Recommendations
    const title = encodeURIComponent(normalizedPaper.title);
    const abstract = encodeURIComponent(normalizedPaper.abstract);
    axios.get(`${API_BASE}/recommend/${paperId}?title=${title}&abstract=${abstract}`)
      .then(res => setRelatedPapers(res.data))
      .catch(() => setRelatedPapers([]))
      .finally(() => setRecsLoading(false));

    // 3. Insights (Feature 2)
    axios.post(`${API_BASE}/extract-insights`, { title: normalizedPaper.title, abstract: normalizedPaper.abstract })
      .then(res => setInsights(res.data))
      .catch(() => setInsights(null))
      .finally(() => setInsightsLoading(false));

    // 4. Citation Graph (Feature 3)
    const encodedId = encodeURIComponent(paperId);
    axios.get(`${API_BASE}/citation-graph/${encodedId}`)
      .then(res => {
        if (res.data && res.data.nodes) {
          setGraphData(res.data);
        } else {
          setGraphData({ nodes: [], links: [] });
        }
      })
      .catch(() => setGraphData({ nodes: [], links: [] }))
      .finally(() => setGraphLoading(false));
  };

  const handleChat = async (question = null) => {
    const q = question || chatInput;
    if (!q.trim() || chatLoading) return;

    const newMessages = [...chatMessages, { role: 'user', content: q }];
    setChatMessages(newMessages);
    setChatInput('');
    setChatLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/chat`, {
        title: selectedPaper.title,
        abstract: selectedPaper.abstract,
        question: q
      });
      setChatMessages([...newMessages, { role: 'ai', content: response.data.answer }]);
    } catch (err) {
      setChatMessages([...newMessages, { role: 'ai', content: "Sorry, I couldn't process that question. Please try again." }]);
    } finally {
      setChatLoading(false);
    }
  };

  const savePaper = async (paper) => {
    try {
      await axios.post(`${API_BASE}/reading-list`, {
        paper_id: paper.id,
        title: paper.title,
        authors: paper.authors,
        abstract: paper.abstract,
        link: paper.link
      });
      alert('Paper saved to reading list!');
      fetchReadingList();
    } catch (err) {
      alert('Failed to save paper.');
    }
  };

  const removePaper = async (paperId) => {
    try {
      await axios.delete(`${API_BASE}/reading-list/${paperId}`);
      fetchReadingList();
    } catch (err) {
      alert('Failed to remove paper.');
    }
  };

  const suggestions = [
    "What is the main contribution?",
    "What dataset was used?",
    "What are the limitations?",
    "Explain the methodology simply"
  ];

  return (
    <ErrorBoundary>
    <div className="app-container">
      <header className="header">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          PaperPilot
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          Your AI-powered research assistant
        </motion.p>
        
        <div className="nav-tabs">
          <button className={`tab ${view === 'search' ? 'active' : ''}`} onClick={() => setView('search')}>Search</button>
          <button className={`tab ${view === 'library' ? 'active' : ''}`} onClick={() => { setView('library'); fetchReadingList(); }}>Library</button>
        </div>
      </header>

      {view === 'search' ? (
        <>
          <form className="search-container" onSubmit={handleSearch}>
            <input 
              type="text" 
              className="search-input"
              placeholder="Enter research topic or abstract..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button type="submit" className="search-button" disabled={loading}>
              {loading ? 'Searching...' : <Search size={20} />}
            </button>
          </form>

          {error && <div className="error-message">{error}</div>}

          <div className="results-grid">
            <AnimatePresence>
              {results.map((paper, index) => (
                <motion.div 
                  key={paper.id}
                  className="paper-card"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.05 }}
                  layout
                  onClick={() => openDetail(paper)}
                >
                  <h3 className="paper-title">{paper.title}</h3>
                  <p className="paper-authors">
                    {Array.isArray(paper.authors) ? paper.authors.join(', ') : paper.authors}
                  </p>
                  <p className="paper-abstract">{paper.abstract}</p>
                  
                  <div className="paper-footer">
                    <span className="relevance-badge">
                      {Math.round(paper.relevance_score * 100)}% Match
                    </span>
                    <div className="card-actions">
                      <button 
                        className={`save-btn ${isSaved(paper.id) ? 'saved' : ''}`} 
                        onClick={(e) => { e.stopPropagation(); savePaper(paper); }}
                        disabled={isSaved(paper.id)}
                      >
                        <BookOpen size={16} />
                        {isSaved(paper.id) ? 'Saved' : 'Save'}
                      </button>
                      <a href={paper.link} target="_blank" rel="noopener noreferrer" className="view-btn" onClick={(e) => e.stopPropagation()}>
                        <ExternalLink size={18} />
                      </a>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </>
      ) : (
        <div className="library-view">
          <div className="dashboard-grid">
            <div className="trend-card">
              <h3><BarChart3 size={20} /> Research Trends</h3>
              {trends && trends.trends && trends.trends.length > 0 ? (
                <Plot
                  data={[{
                    x: (trends?.trends || []).map(t => t.year),
                    y: (trends?.trends || []).map(t => t.count),
                    type: 'scatter',
                    mode: 'lines+markers',
                    marker: { color: '#6366f1' },
                    line: { shape: 'spline' }
                  }]}
                  layout={{
                    autosize: true, height: 300, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
                    font: { color: '#94a3b8' }, margin: { t: 20, r: 20, b: 40, l: 40 },
                    xaxis: { gridcolor: '#334155' }, yaxis: { gridcolor: '#334155' }
                  }}
                  useResizeHandler={true} style={{ width: '100%' }} config={{ displayModeBar: false }}
                />
              ) : <p className="muted">Search for a topic to see trends.</p>}
            </div>

            <div className="history-card">
              <h3><Search size={20} /> Recent Searches</h3>
              <div className="history-list">
                {history.slice(0, 10).map((h, i) => (
                  <div key={i} className="history-item" onClick={() => { setQuery(h?.query || ''); setView('search'); }}>
                    <ChevronRight size={14} />
                    <span>{h?.query || 'Untitled Search'}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          <div className="results-grid">
            {readingList.map((paper) => (
              <div key={paper.paper_id} className="paper-card" onClick={() => openDetail(paper)}>
                <h3 className="paper-title">{paper.title}</h3>
                <p className="paper-authors">{paper.authors}</p>
                <p className="paper-abstract">{paper.abstract}</p>
                <div className="paper-footer">
                  <button className="remove-btn" onClick={(e) => { e.stopPropagation(); removePaper(paper.paper_id); }}>Remove</button>
                  <a href={paper.link} target="_blank" rel="noopener noreferrer" className="view-btn" onClick={(e) => e.stopPropagation()}><ExternalLink size={18} /></a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detail Modal */}
      <AnimatePresence>
        {selectedPaper && (
          <motion.div className="modal-overlay" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setSelectedPaper(null)}>
            <motion.div 
              className="modal-content" initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }} transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              onClick={(e) => e.stopPropagation()}
            >
              <button className="close-btn" onClick={() => setSelectedPaper(null)}><X size={24} /></button>

              <div className="modal-header">
                <span className="badge">AI Literatue Assistant</span>
                <h2 className="modal-title">{selectedPaper.title}</h2>
                <p className="modal-authors">{Array.isArray(selectedPaper.authors) ? selectedPaper.authors.join(', ') : selectedPaper.authors}</p>
              </div>

              <div className="modal-body">
                {/* Feature 2: Insights */}
                <section className="detail-section">
                  <h3><Zap size={20} color="#f59e0b" /> Key Insights</h3>
                  <div className="insights-grid">
                    {insightsLoading ? [1,2,3,4,5].map(i => <div key={i} className="skeleton-card" />) : (
                      <>
                        <div className="insight-card">
                          <h4><Info size={14} /> Methodology</h4>
                          <p>{insights?.methodology || "Not specified"}</p>
                        </div>
                        <div className="insight-card">
                          <h4><BookOpen size={14} /> Dataset</h4>
                          <p>{insights?.dataset || "Not specified"}</p>
                        </div>
                        <div className="insight-card">
                          <h4><Target size={14} /> Key Results</h4>
                          <p>{insights?.key_results || "Not specified"}</p>
                        </div>
                        <div className="insight-card">
                          <h4><AlertCircle size={14} /> Limitations</h4>
                          <p>{insights?.limitations || "Not specified"}</p>
                        </div>
                        <div className="insight-card">
                          <h4><Repeat size={14} /> Future Work</h4>
                          <p>{insights?.future_work || "Not specified"}</p>
                        </div>
                      </>
                    )}
                  </div>
                </section>

                <section className="detail-section">
                  <h3><Sparkles size={20} color="#8b5cf6" /> AI Executive Summary</h3>
                  {summaryLoading ? <div className="skeleton-text">Analyzing abstract...</div> : <p className="ai-summary">{aiSummary}</p>}
                </section>

                {/* Feature 1: Chat with Paper */}
                <section className="detail-section">
                  <h3><MessageSquare size={20} color="#10b981" /> Chat with Paper</h3>
                  <div className="chat-container">
                    <div className="chat-history">
                      {chatMessages.map((msg, i) => (
                        <div key={i} className={`chat-message ${msg.role}`}>
                          {msg.content}
                        </div>
                      ))}
                      {chatLoading && <div className="chat-message ai">Thinking...</div>}
                      <div ref={chatEndRef} />
                    </div>
                    <div className="chat-suggestions">
                      {suggestions.map((s, i) => (
                        <button key={i} className="suggestion-chip" onClick={() => handleChat(s)}>{s}</button>
                      ))}
                    </div>
                    <div className="chat-input-wrapper">
                      <input 
                        className="chat-input" placeholder="Ask anything about this paper..." 
                        value={chatInput} onChange={(e) => setChatInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleChat()}
                      />
                      <button className="send-btn" onClick={() => handleChat()}><Send size={18} /></button>
                    </div>
                  </div>
                </section>

                {/* Feature 3: Citation Graph */}
                <section className="detail-section">
                  <h3><Share2 size={20} color="#6366f1" /> Citation Topology</h3>
                  <div className="graph-container">
                    {graphLoading ? <div className="loading-overlay">Mapping citations...</div> : (
                      graphData.nodes.length > 0 ? (
                        <ForceGraph2D
                          graphData={graphData}
                          width={600}
                          height={400}
                          nodeLabel="title"
                          nodeColor={n => n.color || "#6366f1"}
                          nodeVal={n => n.val || 10}
                          nodeRelSize={4}
                          linkColor={() => '#334155'}
                          backgroundColor="#0f172a"
                          onNodeClick={node => {
                            if (!node.id || String(node.id).startsWith('cite_')) return;
                            window.open(`https://api.semanticscholar.org/paper/${node.id}`, '_blank');
                          }}
                        />
                      ) : <div className="muted" style={{padding: '20px'}}>No citation data found for this paper.</div>
                    )}
                    <div className="graph-hint">Scroll to zoom • Drag to pan • Click purple nodes to view</div>
                  </div>
                </section>

                <section className="detail-section">
                  <h3>Related Research</h3>
                  <div className="related-list">
                    {recsLoading ? <div className="skeleton-text">Finding matches...</div> : relatedPapers.map(rp => (
                      <div key={rp.id} className="related-item" onClick={() => openDetail(rp)}>
                        <ChevronRight size={16} />
                        <div>
                          <h4>{rp.title}</h4>
                          <p>{rp.authors[0]} et al. ({rp.published.substring(0, 4)})</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              </div>
              
              <div className="modal-footer">
                <a href={selectedPaper.link} target="_blank" rel="noopener noreferrer" className="primary-btn">
                  Read Full Paper <ExternalLink size={18} />
                </a>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {loading && (
        <div className="loading">
          <Sparkles className="spin" />
          <p>Semantic analysis in progress...</p>
        </div>
      )}
    </div>
    </ErrorBoundary>
  );
}

export default App;
