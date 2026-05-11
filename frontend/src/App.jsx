import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, BookOpen, ExternalLink, Sparkles, X, ChevronRight, BarChart3, Share2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Plot from 'react-plotly.js';
import './App.css';

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
  const [citations, setCitations] = useState([]);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [recsLoading, setRecsLoading] = useState(false);
  const [citationsLoading, setCitationsLoading] = useState(false);
  const [trends, setTrends] = useState(null);

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
      fetchHistory(); // Refresh history
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
    // Normalize paper object (handle both search results and library items)
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
    setCitations([]);
    
    setSummaryLoading(true);
    setRecsLoading(true);
    setCitationsLoading(true);
    
    const paperId = normalizedPaper.id;
    const title = encodeURIComponent(normalizedPaper.title);
    const abstract = encodeURIComponent(normalizedPaper.abstract);

    // Fetch all in parallel
    axios.post(`${API_BASE}/summarize`, { text: normalizedPaper.abstract })
      .then(res => setAiSummary(res.data.summary))
      .catch(err => {
        console.error(err);
        setAiSummary("Failed to generate AI summary.");
      })
      .finally(() => setSummaryLoading(false));

    axios.get(`${API_BASE}/recommend/${paperId}?title=${title}&abstract=${abstract}`)
      .then(res => setRelatedPapers(res.data))
      .catch(err => {
        console.error(err);
        setRelatedPapers([]);
      })
      .finally(() => setRecsLoading(false));

    axios.get(`${API_BASE}/citations/${paperId}?title=${title}`)
      .then(res => setCitations(res.data))
      .catch(err => {
        console.error(err);
        setCitations([]);
      })
      .finally(() => setCitationsLoading(false));
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
      alert('Failed to save paper or already saved.');
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
          <button 
            className={`tab ${view === 'search' ? 'active' : ''}`}
            onClick={() => setView('search')}
          >
            Search
          </button>
          <button 
            className={`tab ${view === 'library' ? 'active' : ''}`}
            onClick={() => {
              setView('library');
              fetchReadingList();
            }}
          >
            Library
          </button>
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
                        onClick={(e) => {
                          e.stopPropagation();
                          savePaper(paper);
                        }}
                        disabled={isSaved(paper.id)}
                      >
                        <BookOpen size={16} />
                        {isSaved(paper.id) ? 'Saved' : 'Save'}
                      </button>
                      <a 
                        href={paper.link} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="view-btn"
                        onClick={(e) => e.stopPropagation()}
                      >
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
                <div style={{ minHeight: '300px' }}>
                  <Plot
                    data={[
                      {
                        x: (trends?.trends || []).map(t => t.year),
                        y: (trends?.trends || []).map(t => t.count),
                        type: 'scatter',
                        mode: 'lines+markers',
                        marker: { color: '#6366f1' },
                        line: { shape: 'spline' }
                      }
                    ]}
                    layout={{
                      autosize: true,
                      height: 300,
                      paper_bgcolor: 'transparent',
                      plot_bgcolor: 'transparent',
                      font: { color: '#94a3b8' },
                      margin: { t: 20, r: 20, b: 40, l: 40 },
                      xaxis: { gridcolor: '#334155' },
                      yaxis: { gridcolor: '#334155' }
                    }}
                    useResizeHandler={true}
                    style={{ width: '100%', height: '100%' }}
                    config={{ displayModeBar: false }}
                  />
                </div>
              ) : (
                <p className="muted">Search for a topic to see trends.</p>
              )}
            </div>

            <div className="history-card">
              <h3><Search size={20} /> Recent Searches</h3>
              <div className="history-list">
                {history && history.length > 0 ? (
                  history.slice(0, 10).map((h, i) => (
                    <div key={i} className="history-item" onClick={() => { setQuery(h?.query || ''); setView('search'); }}>
                      <ChevronRight size={14} />
                      <span>{h?.query || 'Untitled Search'}</span>
                    </div>
                  ))
                ) : (
                  <p className="muted">No search history yet.</p>
                )}
              </div>
            </div>
          </div>
          
          <div className="results-grid">
            {readingList && readingList.length > 0 ? (
              readingList.map((paper) => (
                <div key={paper.paper_id} className="paper-card" onClick={() => openDetail(paper)}>
                  <h3 className="paper-title">{paper.title}</h3>
                  <p className="paper-authors">
                    {Array.isArray(paper.authors) ? paper.authors.join(', ') : paper.authors}
                  </p>
                  <p className="paper-abstract">{paper.abstract}</p>
                  <div className="paper-footer">
                    <button className="remove-btn" onClick={(e) => {
                      e.stopPropagation();
                      removePaper(paper.paper_id);
                    }}>
                      Remove
                    </button>
                    <a 
                      href={paper.link} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="view-btn"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <ExternalLink size={18} />
                    </a>
                  </div>
                </div>
              ))
            ) : (
              <div className="loading"><p>Your library is empty.</p></div>
            )}
          </div>
        </div>
      )}

      {/* Detail Modal */}
      <AnimatePresence>
        {selectedPaper && (
          <motion.div 
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedPaper(null)}
          >
            <motion.div 
              className="modal-content"
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              onClick={(e) => e.stopPropagation()}
            >
              <button className="close-btn" onClick={() => setSelectedPaper(null)}>
                <X size={24} />
              </button>

              <div className="modal-header">
                <span className="badge">Paper Details</span>
                <h2 className="modal-title">{selectedPaper.title}</h2>
                <p className="modal-authors">{Array.isArray(selectedPaper.authors) ? selectedPaper.authors.join(', ') : selectedPaper.authors}</p>
              </div>

              <div className="modal-body">
                <section className="detail-section">
                  <h3><Sparkles size={20} color="#8b5cf6" /> AI-Generated Summary</h3>
                  {summaryLoading ? (
                    <div className="skeleton-text">Generating summary...</div>
                  ) : (
                    <p className="ai-summary">{aiSummary || "Summary unavailable."}</p>
                  )}
                </section>

                <section className="detail-section">
                  <h3>Abstract</h3>
                  <p>{selectedPaper.abstract}</p>
                </section>

                <section className="detail-section">
                  <h3><Share2 size={20} /> Citation Graph</h3>
                  <div className="citation-container">
                    {citationsLoading ? (
                      <div className="skeleton-text">Analyzing citations...</div>
                    ) : citations.length > 0 ? (
                      <Plot
                        data={[
                          {
                            x: [selectedPaper?.title?.substring(0, 10), ...(citations || []).map(c => c?.title?.substring(0, 10))],
                            y: [10, ...(citations || []).map((_, i) => i)],
                            text: [selectedPaper?.title, ...(citations || []).map(c => c?.title)],
                            mode: 'markers+text',
                            type: 'scatter',
                            marker: { size: 20, color: ['#8b5cf6', ...(citations || []).map(() => '#6366f1')] },
                            textposition: 'top center'
                          }
                        ]}
                        layout={{
                          width: 600,
                          height: 300,
                          paper_bgcolor: 'transparent',
                          plot_bgcolor: 'transparent',
                          xaxis: { visible: false },
                          yaxis: { visible: false },
                          margin: { t: 0, r: 0, b: 0, l: 0 }
                        }}
                      />
                    ) : (
                      <p className="muted">No citations found in recent database.</p>
                    )}
                  </div>
                </section>

                <section className="detail-section">
                  <h3>Related Research</h3>
                  <div className="related-list">
                    {recsLoading ? (
                      <div className="skeleton-text">Finding similar papers...</div>
                    ) : relatedPapers.length > 0 ? (
                      relatedPapers.map(rp => (
                        <div key={rp.id} className="related-item" onClick={() => openDetail(rp)}>
                          <ChevronRight size={16} />
                          <div>
                            <h4>{rp.title}</h4>
                            <p>{rp.authors[0]} et al. ({rp.published.substring(0, 4)})</p>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="muted">No similar research found.</p>
                    )}
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

      {results.length === 0 && !loading && !error && query && (
        <div className="loading">
          <p>No papers found. Try a different query.</p>
        </div>
      )}
    </div>
    </ErrorBoundary>
  );
}

export default App;
