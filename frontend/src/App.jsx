import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { Line, Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler } from 'chart.js';
import { UploadCloud, TrendingUp, Activity, Database, Calendar, RefreshCw, ShoppingCart, ArrowLeft, BarChart2 } from 'lucide-react';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler);

const API_URL = "http://localhost:8000";

function UploadPage() {
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    setStatusMsg("⏳ Uploading and processing dataset...");
    try {
      await axios.post(`${API_URL}/upload/`, formData);
      setStatusMsg("⏳ Upload successful! Training AI model...");
      
      await axios.get(`${API_URL}/train/`);
      setStatusMsg("✅ AI Model trained securely. Redirecting to Dashboard...");
      
      // Navigate to dashboard after 1.5 seconds
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500);

    } catch (err) {
      setStatusMsg(`❌ Error: ${err.response?.data?.detail || err.message}. Make sure backend is running!`);
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-container">
      <div className="navbar">
        <div style={{ flex: 1 }}></div>
        <div className="navbar-title" style={{ textAlign: 'center' }}>
          <h1>AI Demand Predictor</h1>
        </div>
        <div style={{ flex: 1, display: 'flex', justifyContent: 'flex-end' }}>
          <Link to="/dashboard" className="action-btn" style={{width: 'auto'}}>
            View Dashboard <BarChart2 size={18} />
          </Link>
        </div>
      </div>

      <div style={{textAlign: 'center', marginBottom: '3rem'}}>
        <h2 className="page-title">Welcome to Sales AI</h2>
        <p className="subtitle">Learn how to forecast your business sales in 3 easy steps</p>
      </div>

      <div className="tutorial-banner">
        <div className="step-card">
          <div className="step-number">1</div>
          <h3>Upload Historical Data</h3>
          <p>Provide past sales records so the AI can learn your business trends.</p>
        </div>
        <div className="step-card">
          <div className="step-number">2</div>
          <h3>Train the AI Model</h3>
          <p>Our backend automatically trains a Random Forest algorithm securely.</p>
        </div>
        <div className="step-card">
          <div className="step-number">3</div>
          <h3>Generate Forecast</h3>
          <p>Predict future demand and visually analyze the trajectory.</p>
        </div>
      </div>

      <div className="glass-panel" style={{textAlign: 'center', padding: '4rem 2rem'}}>
        <h2 style={{marginBottom: '2rem'}}>Start Step 1: Upload Data</h2>
        
        <input type="file" accept=".csv" ref={fileInputRef} style={{display: 'none'}} onChange={handleFileUpload} />
        
        <div className="upload-area" onClick={() => !loading && fileInputRef.current.click()}>
          <UploadCloud size={64} color="#3b82f6" style={{marginBottom: '1.5rem'}}/>
          <h3 style={{color: 'white', marginBottom: '0.5rem', fontSize: '1.5rem'}}>Click to Upload CSV</h3>
          <p style={{color: 'var(--text-muted)'}}>Drag and drop or click to select your sales dataset.</p>
        </div>

        {statusMsg && (
          <div>
            <span className={`status-badge ${statusMsg.includes('❌') ? 'status-error' : 'status-success'}`}>
              {statusMsg}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

function DashboardPage() {
  const [historicalData, setHistoricalData] = useState([]);
  const [predictionData, setPredictionData] = useState([]);
  const [productData, setProductData] = useState([]);
  const [daysToPredict, setDaysToPredict] = useState(30);
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");

  const fetchData = async () => {
    try {
      const res = await axios.get(`${API_URL}/historical/`);
      setHistoricalData(res.data.data);
      
      const prodRes = await axios.get(`${API_URL}/product-breakdown/`);
      setProductData(prodRes.data.data);
      
      // Auto predict if data exists
      if (res.data.data.length > 0) {
          handlePredict(res.data.data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handlePredict = async (histData) => {
    const dataToCheck = histData || historicalData;
    if (dataToCheck.length === 0) {
      setStatusMsg("❌ No data available. Please go back and upload.");
      return;
    }
    setLoading(true);
    setStatusMsg("🧠 AI is generating forecast...");
    try {
      const res = await axios.get(`${API_URL}/predict/${daysToPredict}`);
      setPredictionData(res.data.predictions);
      setStatusMsg(`✅ Successfully predicted next ${daysToPredict} days.`);
    } catch (err) {
      setStatusMsg(`❌ Prediction failed: ${err.response?.data?.detail || err.message}`);
    }
    setLoading(false);
  };

  const chartLabels = [...historicalData.map(d => d.date), ...predictionData.map(d => d.date)];
  const histSales = historicalData.map(d => d.total_sales);
  const predSales = [...Array(historicalData.length).fill(null), ...predictionData.map(d => d.predicted_sales)];

  const chartData = {
    labels: chartLabels,
    datasets: [
      {
        label: 'Historical Sales',
        data: histSales,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHitRadius: 10,
      },
      {
        label: 'AI Forecast',
        data: predSales,
        borderColor: '#c084fc',
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: '#c084fc',
        pointHitRadius: 10,
      }
    ]
  };

  const chartOptions = {
    responsive: true, maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: { legend: { labels: { color: '#f1f5f9', font: { family: 'Outfit', size: 14 } } }, tooltip: { backgroundColor: 'rgba(15, 23, 42, 0.9)', titleFont: { family: 'Outfit', size: 14 }, padding: 12, borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1 } },
    scales: { x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8', maxTicksLimit: 12 } }, y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8', callback: (value) => '₹' + value.toLocaleString() } } }
  };

  const barChartData = {
    labels: productData.map(d => d.name.replace(/_/g, ' ')),
    datasets: [{
      label: 'Units Sold',
      data: productData.map(d => d.total_units),
      backgroundColor: 'rgba(6, 182, 212, 0.6)', borderColor: '#22d3ee', borderWidth: 1, borderRadius: 4
    }]
  };

  const barOptions = {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false }, tooltip: { backgroundColor: 'rgba(15, 23, 42, 0.9)' } },
    scales: { x: { grid: { display: false }, ticks: { color: '#94a3b8' } }, y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } } }
  };

  const totalRev = historicalData.reduce((sum, item) => sum + item.total_sales, 0);
  const avgRev = historicalData.length > 0 ? totalRev / historicalData.length : 0;
  const predTotal = predictionData.reduce((sum, item) => sum + item.predicted_sales, 0);

  return (
    <div className="dashboard-container">
      <div className="navbar">
        <div style={{ flex: 1 }}>
          <Link to="/" className="nav-link" style={{width: 'fit-content'}}>
            <ArrowLeft size={18} /> Back to Upload
          </Link>
        </div>
        <div className="navbar-title" style={{ textAlign: 'center' }}>
          <h1 style={{fontSize: '2.2rem'}}>Analytics Dashboard</h1>
          <p className="subtitle" style={{fontSize: '0.9rem', marginTop: 0}}>Real-time AI Business Insights</p>
        </div>
        <div style={{ flex: 1 }}></div>
      </div>

      <div className="grid-metrics">
        <div className="glass-panel metric-card">
          <div className="metric-icon icon-blue"><Database size={24} /></div>
          <div className="metric-info">
            <h3>Historical Revenue</h3>
            <p>₹{totalRev.toLocaleString(undefined, {maximumFractionDigits: 0})}</p>
          </div>
        </div>
        <div className="glass-panel metric-card">
          <div className="metric-icon icon-cyan"><Activity size={24} /></div>
          <div className="metric-info">
            <h3>Avg Daily Sales</h3>
            <p>₹{avgRev.toLocaleString(undefined, {maximumFractionDigits: 0})}</p>
          </div>
        </div>
        <div className="glass-panel metric-card">
          <div className="metric-icon icon-purple"><TrendingUp size={24} /></div>
          <div className="metric-info">
            <h3>Predicted Revenue ({daysToPredict} Days)</h3>
            <p>{predTotal > 0 ? '₹'+predTotal.toLocaleString(undefined, {maximumFractionDigits: 0}) : '---'}</p>
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem'}}>
        <div>
          <h2 style={{fontSize: '1.2rem'}}>Forecasting Controls</h2>
          <p style={{color: 'var(--text-muted)', fontSize: '0.9rem'}}>Adjust the number of future days to predict.</p>
        </div>
        <div style={{display: 'flex', gap: '1rem', alignItems: 'center'}}>
          <input 
            type="number" 
            value={daysToPredict} 
            onChange={(e) => setDaysToPredict(e.target.value)}
            style={{background: 'rgba(0,0,0,0.3)', border: '1px solid var(--glass-border)', color: 'white', padding: '0.5rem 1rem', borderRadius: '8px', width: '100px'}}
          />
          <button className="action-btn primary" onClick={() => handlePredict(historicalData)} disabled={loading} style={{width: 'auto'}}>
            {loading ? 'Processing...' : <><RefreshCw size={18} /> Update Forecast</>}
          </button>
        </div>
      </div>

      <div className="glass-panel">
        <h2 style={{marginBottom: '1.5rem'}}>Interactive Sales Trajectory</h2>
        <div className="chart-container">
          {(historicalData.length > 0 || predictionData.length > 0) ? (
            <Line data={chartData} options={chartOptions} />
          ) : (
            <div style={{height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)'}}>
              <p>No data. Go back and upload a dataset.</p>
            </div>
          )}
        </div>
      </div>

      <div className="flex-split">
        <div className="glass-panel">
          <h2 style={{marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px'}}><ShoppingCart color="#22d3ee" /> Units Sold by Product</h2>
          <div className="chart-container" style={{height: '300px'}}>
            {productData.length > 0 ? (
              <Bar data={barChartData} options={barOptions} />
            ) : (
              <div style={{height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)'}}>
                <p>No product data available.</p>
              </div>
            )}
          </div>
        </div>
      </div>

    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
