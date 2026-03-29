import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { ChevronDown, ChevronUp, Loader2 } from 'lucide-react';
import './App.css';

const API_BASE = 'http://localhost:8001/api';
// Map the risk colors for Brutalism: High = Red, Medium = Cream, Low = Taupe
const COLORS = { High: '#e8291a', Medium: '#f0ede6', Low: '#a09890' };

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [explanations, setExplanations] = useState({});
  const [explainingId, setExplainingId] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRisk, setFilterRisk] = useState('All');
  const [activeTab, setActiveTab] = useState('dashboard');

  const handleBackToHome = () => {
    setAnalysis(null);
    setFile(null);
    setExplanations({});
    setSearchTerm('');
    setFilterRisk('All');
    setActiveTab('dashboard');
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) handleFileUpload(e.dataTransfer.files[0]);
  };

  const handleFileUpload = async (selectedFile) => {
    if (!selectedFile) return;
    setFile(selectedFile);
    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    try {
      const response = await axios.post(`${API_BASE}/analyze`, formData);
      setAnalysis(response.data);
      setActiveTab('dashboard');
    } catch (error) {
      console.error("Analysis failed", error);
      alert("Failed to analyze. Ensure the backend is running on port 8001.");
    } finally {
      setLoading(false);
    }
  };

  const getExplanation = async (id, text, riskLevel) => {
    if (explanations[id]) return;
    setExplainingId(id);
    try {
      const response = await axios.post(`${API_BASE}/explain`, { clause: text, risk_level: riskLevel });
      setExplanations(prev => ({ ...prev, [id]: response.data.explanation }));
    } catch (error) {
      console.error("Explanation failed", error);
    } finally {
      setExplainingId(null);
    }
  };

  const filteredClauses = analysis?.clauses?.filter(c => {
    const matchesSearch = c.text.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterRisk === 'All' || c.risk_level === filterRisk;
    return matchesSearch && matchesFilter;
  }) || [];

  const chartData = analysis ? [
    { name: 'High', value: analysis.risk_summary.high },
    { name: 'Medium', value: analysis.risk_summary.medium },
    { name: 'Low', value: analysis.risk_summary.low },
  ].filter(d => d.value > 0) : [];

  const methodData = analysis ? Object.entries(
    analysis.clauses.reduce((acc, c) => { acc[c.method] = (acc[c.method] || 0) + 1; return acc; }, {})
  ).map(([name, value]) => ({ name: name.length > 18 ? name.slice(0, 18) + '…' : name, value })) : [];

  const avgConfidence = analysis ? (analysis.clauses.reduce((s, c) => s + c.confidence, 0) / analysis.clauses.length) : 0;
  const highRiskClauses = analysis?.clauses?.filter(c => c.risk_level === 'High') || [];
  const riskScore = analysis ? Math.round(((analysis.risk_summary.high * 3 + analysis.risk_summary.medium * 1.5) / analysis.total_clauses) * 33.3) : 0;

  return (
    <div className="lb-wrap">
      {/* Navbar directly from Mockup */}
      <div className="lb-nav">
        <div className="lb-logo">LEXSCORE</div>
        <div className="lb-nav-links">
          <span>Features</span>
          <span>Pricing</span>
          <span>Docs</span>
          {!analysis ? (
            <span style={{ color: '#e8291a' }} onClick={() => document.getElementById('fileInput').click()}>Try Now →</span>
          ) : (
            <span style={{ color: '#e8291a' }} onClick={handleBackToHome}>Reset Session ✕</span>
          )}
        </div>
      </div>

      <div className="lb-ticker">
        <div className="lb-ticker-content">
          ★ CONTRACT RISK INTELLIGENCE — CLAUSE-BY-CLAUSE ANALYSIS — POWERED BY LEGALBERT — INSTANT RESULTS ★ &nbsp;&nbsp;&nbsp; ★ HIGH RISK CLAUSES FLAGGED IN SECONDS — PROTECT YOUR INTERESTS ★ &nbsp;&nbsp;&nbsp; ★ CONTRACT RISK INTELLIGENCE — CLAUSE-BY-CLAUSE ANALYSIS — POWERED BY LEGALBERT — INSTANT RESULTS ★
        </div>
      </div>

      {!analysis && !loading ? (
        /* ========== LANDING PAGE MOCKUP ========== */
        <div>
          <style>{`html { scroll-snap-type: y mandatory; }`}</style>
          <div className="lb-hero">
            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6 }}>
              <div className="lb-eyebrow">Legal Intelligence Platform</div>
              <div className="lb-h1">Know Your Risk.<br />Before You Sign.</div>
              <div className="lb-sub">Upload any legal contract and receive clause-by-clause risk analysis. Three-tier classification: High, Medium, Low — with confidence scoring.</div>
              <div className="lb-cta-group">
                <button className="lb-btn-primary" onClick={() => document.getElementById('fileInput').click()}>Analyze Contract</button>
                <button className="lb-btn-secondary">View Demo</button>
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}>
              <div className="lb-hero-right">
                <div className="lb-stat-row">
                  <span className="lb-stat-label">Clauses Processed</span>
                  <span className="lb-stat-val">2,847</span>
                </div>
                <div className="lb-stat-row">
                  <span className="lb-stat-label">High Risk Found</span>
                  <span className="lb-stat-val red">14</span>
                </div>
                <div className="lb-stat-row">
                  <span className="lb-stat-label">System Accuracy</span>
                  <span className="lb-stat-val">94.2%</span>
                </div>
                <div className="lb-stat-row">
                  <span className="lb-stat-label">Processing Time</span>
                  <span className="lb-stat-val">1.3s</span>
                </div>
              </div>
            </motion.div>
          </div>

          <div className="lb-upload-section">
            <div
              className="lb-upload"
              onDragEnter={handleDrag} onDragLeave={handleDrag}
              onDragOver={handleDrag} onDrop={handleDrop}
              onClick={() => document.getElementById('fileInput').click()}
              style={dragActive ? { borderColor: '#f0ede6', background: '#111' } : {}}
            >
              <div style={{ fontSize: '56px', marginBottom: '24px', color: '#e8291a' }}>↑</div>
              <div className="lb-upload-title">Drop your contract here</div>
              <div className="lb-upload-sub">Supports PDF and TXT · Max 10MB</div>
              <input id="fileInput" type="file" hidden onChange={(e) => handleFileUpload(e.target.files[0])} accept=".pdf,.txt" />
            </div>
          </div>

          <div className="lb-section">
            <div className="lb-section-label">Platform Features</div>
            <div className="lb-features">
              <FeatureBox num="01" title="Instant Analysis" desc="Clauses scored in seconds using GPU-accelerated inference." />
              <FeatureBox num="02" title="Risk Classification" desc="Three-tier model: High, Medium, Low with confidence scores." highlight />
              <FeatureBox num="03" title="AI Explanations" desc="Plain-English breakdowns of every legal clause identified." />
              <FeatureBox num="04" title="Hybrid Scoring" desc="Expert keyword rules combined with deep learning." />
              <FeatureBox num="05" title="Clause Inspector" desc="Drill into each clause with full text and risk metadata." highlight />
              <FeatureBox num="06" title="Visual Analytics" desc="Interactive charts for risk distribution across model methods." />
            </div>
          </div>

          <div style={{ padding: '20px 28px', borderTop: '2px solid #f0ede6', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {['LegalBERT', 'PyTorch', 'FastAPI', 'React', 'Gemini AI', 'CUAD Dataset'].map(t => (
              <span key={t} className="lb-badge">{t}</span>
            ))}
          </div>
        </div>
      ) : loading ? (
        /* ========== LOADING ========== */
        <div className="loading-state">
          <Loader2 size={64} className="animate-spin" style={{ margin: '0 auto', color: '#e8291a' }} />
          <div className="loading-title">ANALYZING DOCUMENT</div>
          <div className="loading-sub">Segmenting clauses · Running LegalBERT Inference</div>
        </div>
      ) : (
        /* ========== RESULTS DASHBOARD ========== */
        <div className="dashboard-wrap animate-fade-in">
          <div className="lb-tab-nav">
            {[
              { id: 'dashboard', label: 'Overview' },
              { id: 'clauses', label: 'Clause Inspector' },
              { id: 'source', label: 'Extracted Source' },
            ].map(tab => (
              <button key={tab.id} className={`lb-tab-btn ${activeTab === tab.id ? 'active' : ''}`} onClick={() => setActiveTab(tab.id)}>
                {tab.label}
              </button>
            ))}
          </div>

          {activeTab === 'dashboard' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div className="lb-dash-hero">
                <div>
                  <div className="lb-dash-meta">Overall Risk Score</div>
                  <div className="lb-dash-score" style={{ color: riskScore > 60 ? '#e8291a' : '#f0ede6' }}>
                    {riskScore}<span style={{ fontSize: '32px', color: '#a09890' }}>/100</span>
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div className="lb-dash-meta">Status Verdict</div>
                  <div style={{ fontFamily: 'Playfair Display', fontSize: '24px', color: riskScore > 60 ? '#e8291a' : '#f0ede6' }}>
                    {riskScore > 60 ? 'CRITICAL RISKS DETECTED' : riskScore > 30 ? 'MODERATE OVERSIGHT NEEDED' : 'STANDARD CONTRACT PROFILE'}
                  </div>
                </div>
              </div>

              <div className="metrics-row">
                <MetricCard label="Total Clauses" value={analysis.total_clauses} />
                <MetricCard label="High Risk" value={analysis.risk_summary.high} />
                <MetricCard label="Medium Risk" value={analysis.risk_summary.medium} />
                <MetricCard label="Low Risk" value={analysis.risk_summary.low} />
              </div>

              <div className="charts-row">
                <div className="lb-chart">
                  <h3>Risk Distribution</h3>
                  <ResponsiveContainer width="100%" height={280}>
                    <PieChart>
                      <Pie data={chartData} cx="50%" cy="50%" innerRadius={70} outerRadius={100} paddingAngle={2} dataKey="value">
                        {chartData.map((entry, i) => <Cell key={i} fill={COLORS[entry.name]} />)}
                      </Pie>
                      <RechartsTooltip contentStyle={{ backgroundColor: '#0a0a0a', borderColor: '#f0ede6', borderRadius: '0', fontSize: '11px', fontFamily: 'Courier Prime', color: '#f0ede6' }} itemStyle={{ color: '#f0ede6' }} />
                      <Legend wrapperStyle={{ fontSize: '11px', fontFamily: 'Courier Prime' }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="lb-chart">
                  <h3>Detection Architecture</h3>
                  <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={methodData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                      <XAxis dataKey="name" tick={{ fill: '#a09890', fontSize: 10, fontFamily: 'Courier Prime' }} />
                      <YAxis tick={{ fill: '#a09890', fontSize: 10, fontFamily: 'Courier Prime' }} />
                      <RechartsTooltip contentStyle={{ backgroundColor: '#0a0a0a', borderColor: '#f0ede6', borderRadius: '0', fontSize: '11px', fontFamily: 'Courier Prime' }} />
                      <Bar dataKey="value" fill="#f0ede6" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'clauses' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div className="lb-search-row">
                <input type="text" placeholder="Search clauses identified..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="lb-search-input" />
                <div className="lb-filters">
                  {['All', 'High', 'Medium', 'Low'].map(f => (
                    <button key={f} className={`lb-filter-btn ${filterRisk === f ? 'active' : ''}`} onClick={() => setFilterRisk(f)}>
                      {f}
                    </button>
                  ))}
                </div>
              </div>

              <div className="lb-clause-list">
                {filteredClauses.map(clause => (
                  <ClauseCard key={clause.id} clause={clause} explanation={explanations[clause.id]}
                    onExplain={() => getExplanation(clause.id, clause.text, clause.risk_level)}
                    isExplaining={explainingId === clause.id} />
                ))}
                {filteredClauses.length === 0 && (
                  <div style={{ padding: '40px', textAlign: 'center', color: '#a09890', border: '1px solid #333', margin: '0 28px' }}>NO CLAUSES MATCH YOUR QUERY.</div>
                )}
              </div>
            </motion.div>
          )}

          {activeTab === 'source' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div className="lb-source-box">
                <div className="lb-source-title">Extracted Source Document</div>
                <HeatMapSourceText analysis={analysis} />
              </div>
            </motion.div>
          )}
        </div>
      )}

      {/* Footer */}
      <footer style={{ padding: '24px 28px', borderTop: '2px solid #f0ede6', fontSize: '10px', textTransform: 'uppercase', letterSpacing: '2px', color: '#a09890', textAlign: 'center', scrollSnapAlign: 'end' }}>
        LEXSCORE © 2026 · PSG TECH NLP RESEARCH · FOR EXPERIMENTAL USE ONLY
      </footer>
    </div>
  );
}

// ----------------------------------------------------------------------
// SUB COMPONENTS
// ----------------------------------------------------------------------

function FeatureBox({ num, title, desc, highlight }) {
  return (
    <div className="lb-feat">
      <div className="lb-feat-num" style={highlight ? { color: '#e8291a' } : {}}>{num}</div>
      <div className="lb-feat-title">{title}</div>
      <div className="lb-feat-desc">{desc}</div>
    </div>
  );
}

function MetricCard({ label, value }) {
  return (
    <div className="lb-metric-card">
      <div className="lb-metric-val">{value}</div>
      <div className="lb-metric-lbl">{label}</div>
    </div>
  );
}

function ClauseCard({ clause, explanation, onExplain, isExplaining }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="lb-clause">
      <div className={`lb-clause-head risk-${clause.risk_level.toLowerCase()}`} onClick={() => setIsOpen(!isOpen)}>
        <div className="lb-clause-left">
          <span className="lb-clause-id">{clause.id < 10 ? `0${clause.id}` : clause.id}</span>
          <span className="lb-clause-prev">{clause.text}</span>
        </div>
        <div className="lb-clause-right">
          <span>{clause.risk_level} RISK — {(clause.confidence * 100).toFixed(1)}% CONFIDENCE</span>
          <span>{clause.method}</span>
          {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </div>
      <AnimatePresence>
        {isOpen && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} style={{ overflow: 'hidden' }}>
            <div className="lb-clause-body">
              <p className="lb-clause-text">{clause.text}</p>
              <div className="lb-ai-box">
                {explanation ? (
                  <div>
                    <div className="lb-ai-head">AI Clause Breakdown</div>
                    <div className="lb-ai-text">{explanation}</div>
                  </div>
                ) : (
                  <div className="lb-ai-prompt">
                    <span style={{ fontSize: '11px', color: '#a09890', textTransform: 'uppercase' }}>LexScore AI translation available</span>
                    <button className="lb-btn-primary" onClick={(e) => { e.stopPropagation(); onExplain(); }} disabled={isExplaining}>
                      {isExplaining ? <><Loader2 size={12} className="animate-spin" style={{ display: 'inline', marginRight: '8px' }} /> PROCESSING</> : <>Generate Plain English</>}
                    </button>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function HeatMapSourceText({ analysis }) {
  if (!analysis) return null;
  let combinedHtml = analysis.full_text || "";

  const sortedClauses = [...(analysis.clauses || [])].sort((a, b) => b.text.length - a.text.length);

  sortedClauses.forEach(clause => {
    const escapedText = clause.text.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
    const regex = new RegExp(`(${escapedText})`, 'g');
    // Using brutalism badges (solid backgrounds/borders) instead of glowing text
    combinedHtml = combinedHtml.replace(regex, `<span class="bb-${clause.risk_level.toLowerCase()}">$1</span>`);
  });

  return <pre className="lb-source-text" dangerouslySetInnerHTML={{ __html: combinedHtml }} />;
}

export default App;
