import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Activity, ArrowDownRight, ArrowRight, ArrowUpRight, Boxes, CheckCircle2,
  ChevronDown, CircleHelp, Clock3, Download, FileCheck2, Gauge,
  LayoutDashboard, Menu, Package, Search, Settings2, ShieldCheck,
  Sparkles, Truck, X, Zap, Play, Sun, Cuboid, ChartNoAxesCombined, FileWarning, Atom, Code2, Database, CircleCheck, Home,
} from 'lucide-react';
import {
  Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis,
} from 'recharts';

const API = (import.meta.env.VITE_API_URL || 'https://inventory-ml-engineering-api.onrender.com').replace(/\/$/, '');
const initialRows = [
  { sku: 'ST-2048', name: 'Industrial fasteners', category: 'Components', stock: 1280, reorder: 500, vendor: 'Northstar Supply', price: 2.45, status: 'Healthy' },
  { sku: 'EL-1082', name: 'Control module X2', category: 'Electronics', stock: 86, reorder: 120, vendor: 'Vertex Electric', price: 48.9, status: 'Low stock' },
  { sku: 'PK-3011', name: 'Shipping cartons · L', category: 'Packaging', stock: 0, reorder: 200, vendor: 'Packlane Co.', price: 1.15, status: 'Out of stock' },
  { sku: 'MT-8870', name: 'Steel mounting plate', category: 'Components', stock: 462, reorder: 180, vendor: 'Northstar Supply', price: 7.2, status: 'Healthy' },
  { sku: 'EL-2107', name: 'Optical sensor', category: 'Electronics', stock: 34, reorder: 75, vendor: 'Vertex Electric', price: 26.4, status: 'Low stock' },
  { sku: 'PK-4452', name: 'Protective foam insert', category: 'Packaging', stock: 840, reorder: 300, vendor: 'Packlane Co.', price: 0.82, status: 'Healthy' },
];
const trend = [
  { day: 'May 06', value: 4200 }, { day: 'May 07', value: 3850 },
  { day: 'May 08', value: 5120 }, { day: 'May 09', value: 4680 },
  { day: 'May 10', value: 6240 }, { day: 'May 11', value: 5780 },
  { day: 'May 12', value: 7120 }, { day: 'May 13', value: 6650 },
  { day: 'May 14', value: 7840 }, { day: 'May 15', value: 7380 },
  { day: 'May 16', value: 8620 }, { day: 'May 17', value: 9410 },
];
const money = value => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
const navItems = [
  { name: 'Overview', icon: LayoutDashboard },
  { name: 'Inventory', icon: Boxes },
  { name: 'Forecasting', icon: Activity },
  { name: 'Invoice checks', icon: FileCheck2 },
];

function Status({ value }) {
  const kind = value.toLowerCase().replaceAll(' ', '-');
  return <span className={`status status-${kind}`}><i />{value}</span>;
}

function Metric({ label, value, change, note, icon: Icon, tone }) {
  return (
    <motion.article className="metric-card" whileHover={{ y: -3 }} transition={{ duration: 0.18 }}>
      <div className="metric-top"><span>{label}</span><span className={`metric-icon ${tone}`}><Icon size={17} /></span></div>
      <div className="metric-value">{value}</div>
      <div className="metric-foot"><span className={change.startsWith('+') ? 'metric-change positive' : 'metric-change attention'}>{change.startsWith('+') ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}{change}</span><span>{note}</span></div>
      <div className={`metric-spark ${tone}`} aria-hidden="true"><i /><i /><i /><i /><i /><i /><i /><i /></div>
    </motion.article>
  );
}

function ApiOutput({ result }) {
  const data = result.data || {};
  const freight = result.kind === 'freight';
  const fmt = value => typeof value === 'number' ? new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(value) : (value ?? '—');
  return (
    <div className={`api-output ${result.ok ? 'output-success' : 'output-error'}`} role="status">
      <div className="output-head"><span className="output-state">{result.ok ? <CheckCircle2 size={17} /> : <X size={17} />}</span><div><b>{result.ok ? (freight ? 'Freight estimate ready' : 'Invoice screening complete') : 'Request could not be completed'}</b><small>{result.ok ? 'Live response from the deployed API' : 'Check the service status and try again'}</small></div><span className="http-code">{result.ok ? 'SUCCESS' : 'ERROR'}</span></div>
      {result.ok ? <>
        <div className="output-primary"><small>{freight ? 'Predicted freight cost' : 'Screening result'}</small><strong>{freight ? `$${fmt(data.predicted_freight)}` : (data.status || 'No status returned')}</strong><span>{freight ? `Training records: ${fmt(data.training_rows)} · ${data.data_mode === 'demo' ? 'synthetic demo data' : (data.data_mode || 'source not specified')}` : (data.flagged ? 'Manual review recommended' : 'No configured rule triggered')}</span></div>
        <div className="output-facts">{freight ? <><div><small>Data mode</small><b>{data.data_mode || 'Not specified'}</b></div><div><small>Currency</small><b>{data.currency || 'Training-data unit'}</b></div></> : <><div><small>Amount mismatch</small><b>${fmt(data.dollar_mismatch)}</b></div><div><small>Screening</small><b>{data.flagged ? 'Flagged' : 'Normal'}</b></div></>}</div>
        {freight && data.note && <p className="output-note">{data.note}</p>}
        {!freight && Array.isArray(data.reasons) && <ul className="output-reasons">{data.reasons.map((reason, index) => <li key={index}>{reason}</li>)}</ul>}
        {!freight && data.disclaimer && <p className="output-note">{data.disclaimer}</p>}
      </> : <p className="output-error-copy">{data.detail || data.error || 'The service did not return a successful response. It may still be starting up.'}</p>}
      <details className="raw-response"><summary>View raw JSON response</summary><pre>{JSON.stringify(data, null, 2)}</pre></details>
    </div>
  );
}

function DashboardApp({ onBack }) {
  const [rows, setRows] = useState(initialRows);
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('All items');
  const [apiStatus, setApiStatus] = useState('Connecting');
  const [activeNav, setActiveNav] = useState('Overview');
  const [mobileNav, setMobileNav] = useState(false);
  const [toast, setToast] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [newItem, setNewItem] = useState({ name: '', sku: '', stock: '', reorder: '', vendor: '' });
  const [invoice, setInvoice] = useState({ amount: '1250', expected: '850', actual: '865', delay: '4' });
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);

  const refreshApi = async () => {
    setApiStatus('Connecting');
    try {
      const response = await fetch(`${API}/health`, { signal: AbortSignal.timeout(12000) });
      if (!response.ok) throw new Error('Service unavailable');
      await response.json();
      setApiStatus('Operational');
    } catch {
      setApiStatus('Waking up');
    }
  };

  useEffect(() => { refreshApi(); }, []);
  useEffect(() => {
    const handleKey = event => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        document.querySelector('.search-global input')?.focus();
      }
      if (event.key === 'Escape') { setMobileNav(false); setShowAdd(false); }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, []);

  const filtered = useMemo(() => rows.filter(row =>
    `${row.name} ${row.sku} ${row.vendor} ${row.category}`.toLowerCase().includes(query.toLowerCase()) &&
    (filter === 'All items' || row.status === filter)
  ), [rows, query, filter]);
  const low = rows.filter(row => row.stock > 0 && row.stock <= row.reorder).length;
  const out = rows.filter(row => row.stock === 0).length;
  const totalValue = rows.reduce((sum, row) => sum + row.stock * row.price, 0);
  const totalUnits = rows.reduce((sum, row) => sum + row.stock, 0);
  const notify = message => { setToast(message); window.clearTimeout(notify.timer); notify.timer = window.setTimeout(() => setToast(''), 2800); };

  const jumpTo = name => {
    setActiveNav(name);
    setMobileNav(false);
    const destination = name === 'Inventory' ? 'inventory' : (name === 'Forecasting' || name === 'Invoice checks' ? 'workbench' : null);
    if (destination) document.getElementById(destination)?.scrollIntoView({ behavior: 'smooth' });
    else window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const runPrediction = async kind => {
    setBusy(true);
    setResult(null);
    try {
      const path = kind === 'freight' ? '/predict-freight' : '/validate-invoice';
      const payload = kind === 'freight'
        ? { invoice_dollars: Number(invoice.amount) }
        : { invoice_dollars: Number(invoice.actual), purchase_total_dollars: Number(invoice.expected), average_receiving_delay_days: Number(invoice.delay) };
      const response = await fetch(`${API}${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal: AbortSignal.timeout(25000) });
      const data = await response.json();
      setResult({ kind, ok: response.ok, data });
    } catch {
      setResult({ kind, ok: false, data: { error: 'The API is waking up or unavailable. Try again in a moment.' } });
    } finally { setBusy(false); }
  };

  const addItem = event => {
    event.preventDefault();
    if (!newItem.name.trim() || !newItem.sku.trim()) return;
    if (rows.some(row => row.sku.toLowerCase() === newItem.sku.trim().toLowerCase())) {
      notify('That SKU already exists in this session');
      return;
    }
    const stock = Number(newItem.stock) || 0;
    const reorder = Number(newItem.reorder) || 0;
    setRows(previous => [{ sku: newItem.sku.trim(), name: newItem.name.trim(), category: 'New item', stock, reorder, vendor: newItem.vendor.trim() || 'Unassigned vendor', price: 0, status: stock === 0 ? 'Out of stock' : stock <= reorder ? 'Low stock' : 'Healthy' }, ...previous]);
    setNewItem({ name: '', sku: '', stock: '', reorder: '', vendor: '' });
    setShowAdd(false);
    notify('Item added to this session');
  };

  const exportCsv = () => {
    const csv = ['SKU,Product,Category,Stock,Reorder point,Vendor,Status', ...filtered.map(row => [row.sku, row.name, row.category, row.stock, row.reorder, row.vendor, row.status].map(value => `"${String(value).replaceAll('"', '""')}"`).join(','))].join('\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'stockwise-inventory.csv';
    link.click();
    URL.revokeObjectURL(url);
    notify('Filtered inventory exported');
  };

  return <div className="app-shell">
    <aside className={`sidebar ${mobileNav ? 'sidebar-open' : ''}`}>
      <div className="brand"><div className="brand-mark"><Boxes size={19} /></div><div className="brand-copy"><b>stockwise</b><small>INVENTORY INTELLIGENCE</small></div><button className="mobile-close icon-btn" onClick={() => setMobileNav(false)} aria-label="Close menu"><X size={18} /></button></div>
      <div className="workspace-label">WORKSPACE <span>DEMO</span></div>
      <nav aria-label="Main navigation">{navItems.map(({ name, icon: Icon }) => <button key={name} className={`nav-item ${activeNav === name ? 'active' : ''}`} onClick={() => jumpTo(name)}><Icon size={17} /><span>{name}</span>{name === 'Inventory' && <span className="nav-count">{rows.length}</span>}</button>)}</nav>
      <div className="sidebar-spacer" />
      <div className="sidebar-bottom"><div className="sidebar-note"><div className="note-mark"><Sparkles size={15} /></div><div><b>Make the next move</b><p>Translate stock signals into confident decisions.</p><a href="#workbench">Explore the workbench <ArrowRight size={13} /></a></div></div><button className="nav-item settings-link" onClick={() => notify('Settings are not connected in this demo')}><Settings2 size={17} /><span>Settings</span></button><div className="profile"><div className="avatar">S</div><div className="profile-copy"><b>Stockwise demo</b><small>Sample workspace</small></div><ChevronDown size={15} /></div></div>
      <div className="sidebar-footnote">Built for a clearer view of every moving part.</div>
    </aside>
    {mobileNav && <button className="mobile-backdrop" onClick={() => setMobileNav(false)} aria-label="Close navigation" />}

    <main className="main-area">
      <header className="topbar"><div className="topbar-start"><button className="btn btn-ghost dashboard-home-btn" onClick={onBack} title="Return to Stockwise home"><Home size={15}/> Home</button><button className="mobile-menu icon-btn" onClick={() => setMobileNav(true)} aria-label="Open menu"><Menu size={19} /></button><div className="breadcrumbs">Workspace <span>/</span> <b>{activeNav}</b></div></div><div className="topbar-right"><label className="search-global"><Search size={15} /><input aria-label="Search inventory" placeholder="Search inventory..." value={query} onChange={event => setQuery(event.target.value)} /><kbd>⌘ K</kbd></label><button className="icon-btn help-btn" title="Help" aria-label="Help" onClick={() => notify('Use the live workbench to test API predictions.')}><CircleHelp size={18} /></button><div className="avatar top-avatar" title="Stockwise demo">S</div></div></header>

      <div className="page-wrap">
        <section className="welcome-row"><div><div className="eyebrow"><span className="pulse-dot" /> OPERATIONS SNAPSHOT <span className="eyebrow-divider">/</span> {new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}</div><h1>Good morning.<br /><span>Here's your stock, at a glance.</span></h1><p>A clearer read on inventory health, supplier risk, and what needs attention next.</p></div><div className="welcome-actions"><button className="btn btn-ghost" onClick={refreshApi} disabled={apiStatus === 'Connecting'}><Activity size={15} />{apiStatus === 'Connecting' ? 'Checking…' : 'Refresh status'}</button><button className="btn btn-primary" onClick={() => setShowAdd(true)}><Package size={15} />Add inventory</button></div></section>

        <div className={`api-banner ${apiStatus === 'Operational' ? 'api-good' : 'api-idle'}`}><span className={`api-indicator ${apiStatus === 'Operational' ? 'online' : ''}`} /><div><b>Intelligence API <span>·</span> {apiStatus}</b><small>{apiStatus === 'Operational' ? 'Connected to the deployed FastAPI service' : 'Render free-tier service may need a moment to wake up'}</small></div><a href={`${API}/docs`} target="_blank" rel="noreferrer">Open API docs <ArrowUpRight size={13} /></a></div>

        <section className="metric-grid" aria-label="Inventory key metrics">
          <Metric label="Inventory value" value={money(totalValue)} change="+8.2%" note="vs. prior month · demo" icon={Boxes} tone="violet" />
          <Metric label="Units on hand" value={totalUnits.toLocaleString()} change="+4.6%" note="across all active SKUs" icon={Package} tone="blue" />
          <Metric label="Below reorder point" value={String(low).padStart(2, '0')} change={low ? `${low} to review` : 'All clear'} note="stock needs replenishing" icon={ArrowDownRight} tone="amber" />
          <Metric label="Out of stock" value={String(out).padStart(2, '0')} change={out ? `${out} to replenish` : 'All clear'} note="potential fulfillment risk" icon={ShieldCheck} tone="rose" />
        </section>

        <section className="content-grid">
          <motion.div className="surface chart-surface" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
            <div className="section-title"><div><div className="section-eyebrow">MOVEMENT · LAST 12 PERIODS</div><h2>Inventory throughput</h2><p>Illustrative goods movement across recent periods</p></div><span className="chart-period"><Clock3 size={13} /> 12 periods <ChevronDown size={13} /></span></div>
            <div className="chart-summary"><div><b>9,410</b><span>units moved</span></div><span className="trend"><ArrowUpRight size={14} />12.8% <i>vs previous period</i></span></div>
            <div className="chart-box"><ResponsiveContainer width="100%" height="100%"><AreaChart data={trend} margin={{ top: 14, right: 5, left: -20, bottom: 0 }}><defs><linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#7b6cff" stopOpacity={0.22} /><stop offset="92%" stopColor="#7b6cff" stopOpacity={0} /></linearGradient></defs><CartesianGrid stroke="#edf0f2" strokeDasharray="3 5" vertical={false} /><XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: '#9aa2ae', fontSize: 10 }} dy={10} minTickGap={18} /><Tooltip contentStyle={{ background: '#152238', border: '1px solid #293b57', borderRadius: 10, color: '#f6f8fb', fontSize: 12 }} formatter={value => [`${Number(value).toLocaleString()} units`, 'Throughput']} /><Area type="monotone" dataKey="value" stroke="#7565ed" strokeWidth={2.7} fill="url(#areaFill)" activeDot={{ r: 5, fill: '#7565ed', stroke: '#fff', strokeWidth: 3 }} /></AreaChart></ResponsiveContainer></div>
            <div className="chart-legend"><span><i /> Goods movement</span><span className="chart-demo">Illustrative demo series</span></div>
          </motion.div>

          <div className="right-stack"><div className="surface insight-surface"><div className="section-title compact"><div><div className="section-eyebrow">PRIORITY QUEUE</div><h2>Worth a closer look</h2></div><span className="sparkle-icon"><Sparkles size={16} /></span></div>
            <button className="insight-row" onClick={() => { setFilter('Low stock'); jumpTo('Inventory'); }}><span className="insight-symbol warning"><Zap size={16} /></span><span className="insight-copy"><b>{low} {low === 1 ? 'item' : 'items'} below reorder</b><small>Check suppliers and top up stock.</small></span><ArrowUpRight size={15} /></button>
            <button className="insight-row" onClick={() => { setFilter('Out of stock'); jumpTo('Inventory'); }}><span className="insight-symbol danger"><Package size={16} /></span><span className="insight-copy"><b>{out} {out === 1 ? 'item' : 'items'} out of stock</b><small>Could affect near-term fulfillment.</small></span><ArrowUpRight size={15} /></button>
            <div className="insight-note"><Sparkles size={14} /><span>Run a freight estimate below to put invoice-level costs in context.</span></div>
          </div>
          <div className="surface service-surface"><div className="service-head"><span className="service-icon"><Gauge size={17} /></span><div><b>Freight model</b><small>Prediction service</small></div><span className={`service-status ${apiStatus === 'Operational' ? '' : 'pending'}`}><i />{apiStatus === 'Operational' ? 'LIVE' : 'WAKING'}</span></div><div className="service-stats"><div><small>Algorithm</small><b>Random Forest</b></div><div><small>Runtime</small><b>FastAPI · Python</b></div></div><a href={`${API}/docs`} target="_blank" rel="noreferrer" className="service-link">Inspect API <ArrowUpRight size={13} /></a></div></div>
        </section>

        <section className="surface inventory-surface" id="inventory"><div className="section-title inventory-head"><div><div className="section-eyebrow">STOCK CONTROL</div><h2>Inventory catalogue <span className="table-count">{rows.length} SKUs</span></h2><p>Search stock levels, spot reorder risk, and export the current view.</p></div><button className="btn btn-secondary" onClick={exportCsv}><Download size={14} />Export view</button></div>
          <div className="table-toolbar"><label className="search-table"><Search size={14} /><input aria-label="Search products, SKU, or vendor" placeholder="Search products, SKU, vendor..." value={query} onChange={event => setQuery(event.target.value)} /></label><div className="filter-pills" role="group" aria-label="Filter inventory">{['All items', 'Healthy', 'Low stock', 'Out of stock'].map(item => <button key={item} className={filter === item ? 'selected' : ''} onClick={() => setFilter(item)}>{item}{item === 'All items' && <span>{rows.length}</span>}</button>)}</div></div>
          <div className="table-scroll"><table><thead><tr><th>PRODUCT / SKU</th><th>SUPPLIER</th><th>AVAILABLE</th><th>UNIT COST</th><th>HEALTH</th><th aria-label="Actions" /></tr></thead><tbody>{filtered.map((row, index) => <motion.tr key={row.sku} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: Math.min(index * 0.025, 0.15) }}><td><div className="product-cell"><span className={`product-thumb ${row.category.toLowerCase()}`}>{row.category === 'Electronics' ? '◈' : row.category === 'Packaging' ? '▤' : '⌘'}</span><span className="product-meta"><b>{row.name}</b><small>{row.sku} <i>·</i> {row.category}</small></span></div></td><td className="vendor-cell">{row.vendor}</td><td><div className="stock-cell"><div className="stock-track"><span className={row.status === 'Healthy' ? 'stock-good' : row.status === 'Low stock' ? 'stock-low' : 'stock-none'} style={{ width: `${Math.min(100, row.reorder ? Math.round(row.stock / Math.max(row.reorder * 2, 1) * 100) : 100)}%` }} /></div><b>{row.stock.toLocaleString()}</b></div><small className="reorder-copy">Reorder at {row.reorder.toLocaleString()}</small></td><td className="cost-cell">{money(row.price)}</td><td><Status value={row.status} /></td><td><button className="row-action" title={`Restock ${row.name}`} aria-label={`Quick restock ${row.name}`} onClick={() => { setRows(previous => previous.map(item => item.sku === row.sku ? { ...item, stock: item.stock + Math.max(item.reorder, 50), status: 'Healthy' } : item)); notify(`${row.name} restocked in this session`); }}><ArrowUpRight size={14} /></button></td></motion.tr>)}{filtered.length === 0 && <tr><td colSpan="6" className="no-results"><Search size={17} /><b>No matching inventory</b><span>Try another search or clear the status filter.</span><button onClick={() => { setQuery(''); setFilter('All items'); }}>Clear filters</button></td></tr>}</tbody></table></div>
          <div className="table-footer"><span>Showing <b>{filtered.length}</b> of {rows.length} sample items</span><span><i className="footer-dot" /> Demo values · edits last for this session</span></div>
        </section>

        <section className="workbench-section" id="workbench"><div className="workbench-heading"><div><div className="section-eyebrow">LIVE API WORKBENCH</div><h2>Turn signals into decisions.</h2><p>Test requests against the deployed FastAPI service.</p></div><span className="workbench-chip"><Activity size={13} />Interactive</span></div><div className="workbench-grid">
          <div className="surface tool-card"><div className="tool-title"><span className="tool-icon purple"><Truck size={18} /></span><div><h3>Freight cost estimator</h3><p>Estimate freight from invoice value.</p></div></div><label>Invoice amount <span className="field-unit">USD</span><input type="number" min="0" max="1000000000" step="0.01" value={invoice.amount} onChange={event => setInvoice({ ...invoice, amount: event.target.value })} /></label><button className="btn btn-primary full-btn" disabled={busy || !invoice.amount} onClick={() => runPrediction('freight')}>{busy ? 'Running model…' : 'Run freight estimate'}<ArrowRight size={15} /></button>{result?.kind === 'freight' && <ApiOutput result={result} />}</div>
          <div className="surface tool-card"><div className="tool-title"><span className="tool-icon orange"><FileCheck2 size={18} /></span><div><h3>Invoice screening</h3><p>Check totals and receiving delay.</p></div></div><div className="two-fields"><label>Expected total <span className="field-unit">USD</span><input type="number" min="0" max="1000000000" step="0.01" value={invoice.expected} onChange={event => setInvoice({ ...invoice, expected: event.target.value })} /></label><label>Actual total <span className="field-unit">USD</span><input type="number" min="0" max="1000000000" step="0.01" value={invoice.actual} onChange={event => setInvoice({ ...invoice, actual: event.target.value })} /></label></div><label>Receiving delay <span className="field-unit">DAYS</span><input type="number" min="0" max="36500" step="1" value={invoice.delay} onChange={event => setInvoice({ ...invoice, delay: event.target.value })} /></label><button className="btn btn-primary full-btn" disabled={busy || !invoice.expected || !invoice.actual || !invoice.delay} onClick={() => runPrediction('invoice')}>{busy ? 'Checking invoice…' : 'Screen this invoice'}<ArrowRight size={15} /></button>{result?.kind === 'invoice' && <ApiOutput result={result} />}</div>
        </div><p className="workbench-disclaimer"><ShieldCheck size={14} /> Demo only: freight results may use synthetic training data. Invoice flags are review signals, not proof of fraud.</p></section>

        <footer className="footer"><div className="footer-brand"><div className="brand-mark"><Boxes size={15} /></div><b>stockwise</b><span>Inventory intelligence, made actionable.</span></div><div><a href="https://github.com/Corvus06655/inventory-ml-engineering" target="_blank" rel="noreferrer">GitHub <ArrowUpRight size={12} /></a><a href={`${API}/docs`} target="_blank" rel="noreferrer">API docs <ArrowUpRight size={12} /></a><span>© {new Date().getFullYear()} Stockwise</span></div></footer>
      </div>
    </main>

    {showAdd && <div className="modal-backdrop" onMouseDown={event => { if (event.target === event.currentTarget) setShowAdd(false); }}><form className="modal" onSubmit={addItem}><div className="modal-heading"><div><div className="section-eyebrow">STOCK CONTROL</div><h2>Add inventory item</h2><p>Build out your sample catalogue.</p></div><button type="button" className="icon-btn" onClick={() => setShowAdd(false)} aria-label="Close dialog"><X size={17} /></button></div><label>Product name<input required maxLength="80" value={newItem.name} onChange={event => setNewItem({ ...newItem, name: event.target.value })} placeholder="e.g. Steel brackets" /></label><div className="two-fields"><label>SKU<input required maxLength="32" value={newItem.sku} onChange={event => setNewItem({ ...newItem, sku: event.target.value })} placeholder="ST-2001" /></label><label>Stock quantity<input type="number" min="0" step="1" value={newItem.stock} onChange={event => setNewItem({ ...newItem, stock: event.target.value })} placeholder="0" /></label></div><div className="two-fields"><label>Reorder point<input type="number" min="0" step="1" value={newItem.reorder} onChange={event => setNewItem({ ...newItem, reorder: event.target.value })} placeholder="100" /></label><label>Supplier<input maxLength="80" value={newItem.vendor} onChange={event => setNewItem({ ...newItem, vendor: event.target.value })} placeholder="Supplier name" /></label></div><div className="modal-actions"><button type="button" className="btn btn-ghost" onClick={() => setShowAdd(false)}>Cancel</button><button type="submit" className="btn btn-primary">Add to catalogue <ArrowRight size={15} /></button></div><p className="modal-note">Demo workspace only. Items are stored in this browser session, not a database.</p></form></div>}
    {toast && <div className="toast" role="status"><CheckCircle2 size={17} />{toast}</div>}
  </div>;
}

const WAREHOUSE_VIDEO = 'https://videos.pexels.com/video-files/32386624/32386624-hd_1920_1080_25fps.mp4';
const FEATURE_CARDS = [
  { title: 'Inventory Control', description: 'Know what is moving, what is running low, and what needs attention.', image: 'https://images.pexels.com/photos/4483610/pexels-photo-4483610.jpeg?auto=compress&cs=tinysrgb&w=1000', icon: Boxes, tag: 'STOCK VISIBILITY' },
  { title: 'Freight Cost Prediction', description: 'Estimate shipping cost from invoice value with the deployed model API.', image: 'https://images.pexels.com/photos/2199293/pexels-photo-2199293.jpeg?auto=compress&cs=tinysrgb&w=1000', icon: Truck, tag: 'MODEL INFERENCE' },
  { title: 'Invoice Risk Screening', description: 'Surface invoice mismatch and receiving-delay rules for manual review.', image: 'https://images.pexels.com/photos/6863183/pexels-photo-6863183.jpeg?auto=compress&cs=tinysrgb&w=1000', icon: FileWarning, tag: 'RULE-BASED CHECKS' },
  { title: 'Interactive Analytics', description: 'Explore stock signals, summary metrics and trend visualizations.', image: 'https://images.pexels.com/photos/7567443/pexels-photo-7567443.jpeg?auto=compress&cs=tinysrgb&w=1000', icon: ChartNoAxesCombined, tag: 'DECISION SUPPORT' },
];

function LandingPage({ onExplore }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [demoOpen, setDemoOpen] = useState(false);
  const [apiHealth, setApiHealth] = useState('Checking');
  const [healthData, setHealthData] = useState(null);
  useEffect(() => {
    let active = true;
    fetch(`${API}/health`, { signal: AbortSignal.timeout(10000) })
      .then(response => { if (!response.ok) throw new Error('API unavailable'); return response.json(); })
      .then(data => { if (active) { setHealthData(data); setApiHealth(data.status === 'ok' ? 'API reachable' : 'Check API'); } })
      .catch(() => { if (active) setApiHealth('Waking up'); });
    return () => { active = false; };
  }, []);
  useEffect(() => {
    if (!demoOpen) return undefined;
    const onKey = event => { if (event.key === 'Escape') setDemoOpen(false); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [demoOpen]);
  const go = id => { setMenuOpen(false); document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' }); };
  const inStock = 78, lowStock = 15, outStock = 7;
  return <div className="landing">
    <header className="landing-nav">
      <a className="landing-brand" href="#home" onClick={e => { e.preventDefault(); go('home'); }} aria-label="Stockwise home"><span className="cube-logo"><Cuboid size={25}/></span><span>STOCK<span>WISE</span></span></a>
      <button className="landing-mobile-toggle" onClick={() => setMenuOpen(v => !v)} aria-expanded={menuOpen} aria-label="Toggle navigation">{menuOpen ? <X/> : <Menu/>}</button>
      <nav className={menuOpen ? 'landing-links open' : 'landing-links'} aria-label="Landing navigation">
        <a className="active" href="#home" onClick={e => {e.preventDefault();go('home')}}>Home</a>
        <a href="#features" onClick={e => {e.preventDefault();go('features')}}>Features</a>
        <button onClick={() => {setMenuOpen(false);onExplore()}}>Dashboard</button>
        <a href="#technology" onClick={e => {e.preventDefault();go('technology')}}>Technology</a>
        <a href="#about" onClick={e => {e.preventDefault();go('about')}}>About</a>
      </nav>
      <div className="landing-nav-actions"><span className="api-mini"><i className={apiHealth==='API reachable'?'online':''}/>{apiHealth}</span><button className="landing-cta" onClick={onExplore}>Explore Dashboard <ArrowRight size={15}/></button></div>
    </header>

    <section className="landing-hero" id="home">
      <div className="hero-video-wrap" aria-hidden="true">
        <video className="hero-video" autoPlay muted loop playsInline preload="metadata" poster="https://images.pexels.com/photos/4483610/pexels-photo-4483610.jpeg?auto=compress&cs=tinysrgb&w=1800">
          <source src={WAREHOUSE_VIDEO} type="video/mp4"/>
        </video>
      </div>
      <div className="hero-grid-overlay" aria-hidden="true"/>
      <div className="hero-content">
        <motion.div className="hero-copy" initial={{opacity:0,y:22}} animate={{opacity:1,y:0}} transition={{duration:.65}}>
          <div className="hero-kicker"><span/> AI <b>·</b> INVENTORY <b>·</b> SUPPLY CHAIN</div>
          <h1>Smarter <em>Inventory</em><br/>for a Bigger Tomorrow.</h1>
          <p>Predict freight costs, monitor inventory health, and identify invoice anomalies with one intelligent supply-chain platform.</p>
          <div className="hero-actions"><button className="hero-primary" onClick={onExplore}>Explore Dashboard <ArrowRight size={17}/></button><button className="hero-secondary" onClick={() => setDemoOpen(true)}><span><Play size={13} fill="currentColor"/></span> Watch Demo</button></div>
          <div className="hero-proof"><div><b>3+</b><span>Analysis workflows</span></div><div><b>API</b><span>Live request testing</span></div><div><b>End-to-End</b><span>Supply-chain view</span></div></div>
        </motion.div>
        <motion.div className="hero-panels" initial={{opacity:0,x:26}} animate={{opacity:1,x:0}} transition={{duration:.8,delay:.15}}>
          <div className="float-panel health-panel">
            <div className="float-panel-title"><b>Inventory Health</b><span>ILLUSTRATIVE</span></div>
            <div className="health-content"><div className="health-ring"><div><b>{inStock}%</b><small>In Stock</small></div></div><div className="health-legend"><div><i className="lime-dot"/><span>In Stock</span><b>{inStock}%</b></div><div><i className="amber-dot"/><span>Low Stock</span><b>{lowStock}%</b></div><div><i className="red-dot"/><span>Out of Stock</span><b>{outStock}%</b></div></div></div>
          </div>
          <div className="hero-panel-row">
            <div className="float-panel freight-panel"><div className="float-panel-title"><b>Freight Cost Prediction</b><span>API TOOL</span></div><div className="freight-mock"><div className="freight-value"><small>Invoice input</small><b>$1,250</b><span>Try a real request below</span></div><svg viewBox="0 0 260 90" role="img" aria-label="Illustrative freight trend line"><defs><linearGradient id="heroLineFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#b8ff64" stopOpacity=".24"/><stop offset="100%" stopColor="#b8ff64" stopOpacity="0"/></linearGradient></defs><path d="M0 76 L24 62 L40 67 L62 43 L82 51 L102 29 L123 37 L145 18 L162 27 L184 13 L207 24 L230 7 L260 12 L260 90 L0 90Z" fill="url(#heroLineFill)"/><path d="M0 76 L24 62 L40 67 L62 43 L82 51 L102 29 L123 37 L145 18 L162 27 L184 13 L207 24 L230 7 L260 12" fill="none" stroke="#b8ff64" strokeWidth="2.3" strokeLinecap="round" strokeLinejoin="round"/></svg></div><div className="panel-footnote">Trend graphic is illustrative, not model output.</div></div>
            <div className="float-panel invoice-panel"><div className="float-panel-title"><b>Invoice Risk Scan</b><span>RULES</span></div><div className="invoice-alert"><FileWarning size={27}/><div><b>Rule-based review</b><small>Mismatch + delay checks</small></div></div><div className="invoice-mini-row"><span>Invoice total</span><b>Compare</b></div><div className="invoice-mini-row"><span>Receiving delay</span><b>Screen</b></div><button onClick={onExplore}>Open workbench <ArrowRight size={13}/></button></div>
          </div>
          <div className="hero-panel-caption"><span className="caption-dot"/> Sample interface preview <span>·</span> Demo values are labelled</div>
        </motion.div>
      </div>
      <button className="scroll-cue" onClick={() => go('features')} aria-label="Scroll to features"><span/> Scroll to explore</button>
    </section>

    <section className="tech-strip" id="technology"><div className="tech-strip-label">BUILT WITH THE PROJECT'S TECHNOLOGY</div><div className="tech-items"><div><Atom/><span>React</span></div><div><Code2/><span>Python</span></div><div><Activity/><span>FastAPI</span></div><div><Database/><span>SQLite / pandas</span></div><div><ChartNoAxesCombined/><span>scikit-learn</span></div><div><Boxes/><span>Recharts</span></div></div></section>

    <section className="feature-section" id="features"><div className="section-heading"><div><span className="section-tag">CAPABILITIES / 01—04</span><h2>Every signal.<br/><em>One clear picture.</em></h2></div><p>From inventory visibility to invoice-level checks, Stockwise brings the project's tools into one focused workspace.</p></div>
      <div className="feature-grid">{FEATURE_CARDS.map((feature,index)=>{const Icon=feature.icon;return <motion.article className="feature-card" key={feature.title} initial={{opacity:0,y:18}} whileInView={{opacity:1,y:0}} viewport={{once:true,amount:.15}} transition={{duration:.42,delay:index*.07}}><div className="feature-image"><img src={feature.image} alt="" loading="lazy"/><span className="feature-image-shade"/><span className="feature-index">0{index+1}</span><span className="feature-icon"><Icon size={21}/></span></div><div className="feature-copy"><span className="feature-tag">{feature.tag}</span><h3>{feature.title}</h3><p>{feature.description}</p><button onClick={onExplore}>Explore capability <ArrowRight size={14}/></button></div></motion.article>})}</div>
    </section>

    <section className="about-section" id="about"><div className="about-orbit" aria-hidden="true"><div/><div/><div/><GlobeIcon/></div><div className="about-copy"><span className="section-tag">↗ WHY STOCKWISE</span><h2>AI-powered supply-chain <em>intelligence.</em></h2><p>Connect inventory signals, freight-cost estimation, and invoice screening in one accessible demo platform. Move from a raw number to a more informed next step.</p><div className="about-pills"><span><CircleCheck size={15}/> Clear data provenance</span><span><CircleCheck size={15}/> Transparent demo limits</span><span><CircleCheck size={15}/> Real API requests</span></div></div></section>

    <section className="workflow-section"><div className="section-tag">HOW IT WORKS</div><h2>From signal to next step.</h2><div className="workflow-grid"><div><span>01</span><b>Inspect</b><p>Review illustrative stock health and item-level signals.</p></div><div><span>02</span><b>Estimate</b><p>Send invoice value to the deployed freight endpoint.</p></div><div><span>03</span><b>Screen</b><p>Check invoice mismatch and receiving delay with transparent rules.</p></div><div><span>04</span><b>Act</b><p>Use the result to guide a human review—not automate decisions blindly.</p></div></div></section>

    <section className="landing-bottom-cta"><div><span className="section-tag">YOUR OPERATIONS WORKSPACE</span><h2>Make the next move <em>with clarity.</em></h2><p>Open the interactive dashboard to search sample inventory, export a CSV, and test the live API tools.</p></div><button className="hero-primary" onClick={onExplore}>Explore Dashboard <ArrowRight size={17}/></button></section>
    <footer className="landing-footer"><a className="landing-brand" href="#home" onClick={e=>{e.preventDefault();go('home')}}><span className="cube-logo"><Cuboid size={23}/></span><span>STOCK<span>WISE</span></span></a><p>Inventory & Vendor Intelligence · Demo environment</p><div><a href="https://github.com/Corvus06655/inventory-ml-engineering" target="_blank" rel="noreferrer">GitHub <ArrowUpRight size={13}/></a><a href={`${API}/docs`} target="_blank" rel="noreferrer">API Docs <ArrowUpRight size={13}/></a><span>API: {apiHealth}{healthData?.data_mode ? ` · ${healthData.data_mode} mode` : ''}</span></div></footer>

    {demoOpen && <div className="demo-modal-backdrop" role="presentation" onMouseDown={event=>{if(event.target===event.currentTarget)setDemoOpen(false)}}><section className="demo-modal" role="dialog" aria-modal="true" aria-labelledby="demo-title"><button className="demo-modal-close" onClick={()=>setDemoOpen(false)} aria-label="Close demo"><X/></button><div className="demo-modal-video"><video autoPlay muted loop playsInline controls poster="https://images.pexels.com/photos/4483610/pexels-photo-4483610.jpeg?auto=compress&cs=tinysrgb&w=1400"><source src={WAREHOUSE_VIDEO} type="video/mp4"/></video></div><div className="demo-modal-copy"><span className="section-tag">STOCKWISE / WALKTHROUGH</span><h2 id="demo-title">See the supply chain in motion.</h2><p>This is warehouse footage, not a recorded product walkthrough. Explore the dashboard for real API interactions and sample inventory tools.</p><button className="hero-primary" onClick={()=>{setDemoOpen(false);onExplore()}}>Open interactive dashboard <ArrowRight size={16}/></button></div></section></div>}
  </div>;
}
function GlobeIcon(){return <svg viewBox="0 0 120 120" aria-hidden="true"><circle cx="60" cy="60" r="48" fill="none" stroke="currentColor" strokeOpacity=".6"/><ellipse cx="60" cy="60" rx="22" ry="48" fill="none" stroke="currentColor" strokeOpacity=".45"/><ellipse cx="60" cy="60" rx="48" ry="18" fill="none" stroke="currentColor" strokeOpacity=".45"/><path d="M14 60h92M22 38h76M22 82h76" fill="none" stroke="currentColor" strokeOpacity=".45"/></svg>}

export default function App() {
  const [showDashboard,setShowDashboard] = useState(false);
  useEffect(()=>{document.title=showDashboard?'Stockwise — Interactive Dashboard':'Stockwise — AI Supply Chain Intelligence';window.scrollTo({top:0,behavior:'instant'});},[showDashboard]);
  return showDashboard ? <DashboardApp onBack={()=>{setShowDashboard(false);window.scrollTo({top:0,behavior:'instant'});}}/> : <LandingPage onExplore={()=>{setShowDashboard(true);window.scrollTo({top:0,behavior:'instant'});}}/>;
}
