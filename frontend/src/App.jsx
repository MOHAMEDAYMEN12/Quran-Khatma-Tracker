import React, { createContext, useState, useEffect, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { surahs, getAyahIndex, getSurahFromIndex } from './surahData';
import QuranReader from './QuranReader';
import JuzReader from './JuzReader';
import './index.css';
import './i18n';

const API_BASE = 'http://localhost:5000/api';

// --- AUTH CONTEXT ---
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user')) || null);
  const [token, setToken] = useState(localStorage.getItem('token') || null);

  const login = (userData, userToken) => {
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('token', userToken);
    setUser(userData);
    setToken(userToken);
  };

  const logout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    setUser(null);
    setToken(null);
  };

  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          logout();
        }
        return Promise.reject(error);
      }
    );
    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// --- COMPONENTS ---

const Navbar = () => {
  const { user, logout } = useContext(AuthContext);
  const { t, i18n } = useTranslation();

  const toggleLanguage = () => {
    const nextLng = i18n.language === 'tr' ? 'ar' : 'tr';
    i18n.changeLanguage(nextLng);
    document.documentElement.dir = nextLng === 'ar' ? 'rtl' : 'ltr';
  };

  return (
    <nav>
      <div className="logo" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <span style={{ fontSize: '1.8rem' }}>🕌</span>
        <h2 style={{ color: '#3b82f6', margin: 0 }}>Hayırhah</h2>
      </div>
      {user && (
        <div style={{ display: 'flex', gap: '1.5rem', margin: '0 2rem' }} className="nav-links">
          <Link to="/" style={{ color: 'var(--text-main)', textDecoration: 'none', fontWeight: 600 }}>{t('individual_khatms')}</Link>
          <Link to="/group-khatms" style={{ color: 'var(--text-main)', textDecoration: 'none', fontWeight: 600 }}>{t('group_khatms')}</Link>
        </div>
      )}
      <div className="nav-actions">
        <button className="lang-btn" onClick={toggleLanguage}>
          {i18n.language === 'tr' ? t('arabic') : t('turkish')}
        </button>
        {user && (
          <>
            <span style={{ margin: '0 1rem', color: '#94a3b8' }}>{user.name}</span>
            <button variant="secondary" onClick={logout}>{t('logout')}</button>
          </>
        )}
      </div>
    </nav>
  );
};

const Register = () => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({ name: '', email: '', password: '' });
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/auth/register`, formData);
      alert('Success! Please login.');
      navigate('/login');
    } catch (err) {
      alert(err.response?.data?.error || 'Error');
    }
  };

  return (
    <div className="auth-container">
      <h2>{t('register')}</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>{t('name')}</label>
          <input type="text" required onChange={(e) => setFormData({...formData, name: e.target.value})} />
        </div>
        <div className="form-group">
          <label>{t('email')}</label>
          <input type="email" required onChange={(e) => setFormData({...formData, email: e.target.value})} />
        </div>
        <div className="form-group">
          <label>{t('password')}</label>
          <input type="password" required onChange={(e) => setFormData({...formData, password: e.target.value})} />
        </div>
        <button type="submit" style={{width: '100%'}}>{t('register')}</button>
        <p style={{marginTop: '1rem'}}><Link to="/login" style={{color: '#3b82f6'}}>{t('login')}</Link></p>
      </form>
    </div>
  );
};

const Login = () => {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API_BASE}/auth/login`, { email, password });
      login(res.data.user, res.data.token);
      navigate('/');
    } catch (err) {
      alert(err.response?.data?.error || 'Error');
    }
  };

  return (
    <div className="auth-container">
      <h2>{t('login')}</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>{t('email')}</label>
          <input type="email" required onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div className="form-group">
          <label>{t('password')}</label>
          <input type="password" required onChange={(e) => setPassword(e.target.value)} />
        </div>
        <button type="submit" style={{width: '100%'}}>{t('login')}</button>
        <p style={{marginTop: '1rem'}}><Link to="/register" style={{color: '#3b82f6'}}>{t('register')}</Link></p>
      </form>
    </div>
  );
};

const Dashboard = () => {
  const { t } = useTranslation();
  const { token, user } = useContext(AuthContext);
  const [khatms, setKhatms] = useState([]);
  const [newTitle, setNewTitle] = useState('');
  const [newTarget, setNewTarget] = useState('');

  const fetchKhatms = async () => {
    try {
      const res = await axios.get(`${API_BASE}/khatms`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setKhatms(res.data);
    } catch (err) { console.error(err); }
  };

  useEffect(() => { fetchKhatms(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/khatms`, 
        { title: newTitle, target_person: newTarget, type: newTarget ? 'other' : 'self' },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setNewTitle(''); setNewTarget('');
      fetchKhatms();
    } catch (err) { 
      alert('Error creating khatm: ' + (err.response?.data?.error || err.message)); 
      console.error(err);
    }
  };

  const handleUpdate = async (id, lastAyah) => {
    if (lastAyah < 0 || lastAyah > 6236) return alert('Invalid Ayah');
    try {
      await axios.put(`${API_BASE}/khatms/${id}`, 
        { last_ayah: lastAyah },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchKhatms();
    } catch (err) { alert('Update failed'); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Bu hatmi silmek istediğinize emin misiniz?')) return;
    try {
      await axios.delete(`${API_BASE}/khatms/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchKhatms();
    } catch (err) { alert('Delete failed'); }
  };

  const selfKhatms = khatms.filter(k => k.type === 'self');
  const otherKhatms = khatms.filter(k => k.type === 'other');

  return (
    <div className="container">
      <div className="auth-container" style={{maxWidth: '100%', margin: '1rem 0', textAlign: 'left'}}>
        <h3>{t('start_khatm')}</h3>
        <form onSubmit={handleCreate} style={{display: 'flex', gap: '1rem', marginTop: '1rem'}}>
          <input placeholder="Title (e.g. Ramazan Khatm)" value={newTitle} onChange={(e) => setNewTitle(e.target.value)} required />
          <input placeholder="Target Person (Optional)" value={newTarget} onChange={(e) => setNewTarget(e.target.value)} />
          <button type="submit">{t('start_khatm')}</button>
        </form>
      </div>

      <h3 className="section-title">📖 {t('my_khatms')}</h3>
      <div className="khatm-grid">
        {selfKhatms.map(k => <KhatmCard key={k.id} khatm={k} onUpdate={handleUpdate} onDelete={handleDelete} />)}
      </div>

      <h3 className="section-title">👤 {t('other_khatms')}</h3>
      <div className="khatm-grid">
        {otherKhatms.map(k => <KhatmCard key={k.id} khatm={k} onUpdate={handleUpdate} onDelete={handleDelete} />)}
      </div>
    </div>
  );
};

const KhatmCard = ({ khatm, onUpdate, onDelete }) => {
  const { t, i18n } = useTranslation();
  const currentLang = i18n.language;
  const { surah: currentSurah, ayah: currentAyah } = getSurahFromIndex(khatm.last_ayah);
  
  const [selectedSurahId, setSelectedSurahId] = useState(currentSurah.id);
  const [selectedAyah, setSelectedAyah] = useState(currentAyah);

  const percentage = Math.round((khatm.last_ayah / 6236) * 100);

  // Choosing color based on progress
  let barColor = 'blue';
  if (percentage > 50) barColor = 'green';
  if (percentage > 85) barColor = 'yellow';

  const surahOptions = surahs.map(s => (
    <option key={s.id} value={s.id}>
      {currentLang === 'ar' ? s.name : s.nameTr}
    </option>
  ));

  const surah = surahs.find(s => s.id === parseInt(selectedSurahId));
  const ayahOptions = Array.from({ length: surah?.ayahs || 0 }, (_, i) => i + 1).map(a => (
    <option key={a} value={a}>{a}</option>
  ));

  const handleSave = () => {
    const globalIndex = getAyahIndex(parseInt(selectedSurahId), parseInt(selectedAyah));
    onUpdate(khatm.id, globalIndex);
  };

  return (
    <div className="khatm-card">
      <div className="khatm-card-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h3 style={{fontSize: '1.2rem', fontWeight: '700'}}>{khatm.title}</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="percentage" style={{ margin: 0 }}>{percentage}% {t('completed')}</span>
          <button 
            onClick={() => onDelete(khatm.id)} 
            style={{
              background: 'transparent', 
              border: 'none', 
              color: '#ef4444', 
              fontSize: '1.2rem', 
              cursor: 'pointer',
              padding: '0',
              display: 'flex',
              alignItems: 'center'
            }}
            title="Sil / Delete"
          >
            ✕
          </button>
        </div>
      </div>
      
      {khatm.target_person && (
        <div style={{color: 'var(--accent-blue)', fontSize: '0.8rem', marginBottom: '0.5rem', fontWeight: '600'}}>
          👤 {khatm.target_person}
        </div>
      )}

      <div className="progress-container">
        <div className={`progress-bar ${barColor}`} style={{ width: `${percentage}%` }}></div>
      </div>

      <div className="khatm-info" style={{marginBottom: '1rem'}}>
        <span>
          {currentLang === 'ar' ? currentSurah.name : currentSurah.nameTr} : {currentAyah}
        </span>
        <span style={{opacity: 0.6}}>{khatm.last_ayah} / 6236</span>
      </div>

      <div className="update-section" style={{flexDirection: 'column', gap: '0.8rem'}}>
        <div style={{display: 'flex', gap: '0.5rem'}}>
          <select 
            className="update-input" 
            value={selectedSurahId} 
            onChange={(e) => {
              setSelectedSurahId(e.target.value);
              setSelectedAyah(1); // Reset ayah when surah changes
            }}
            style={{flex: 2, background: 'var(--input-bg)', color: 'white', border: '1px solid var(--border)', borderRadius: '8px', padding: '0.5rem'}}
          >
            {surahOptions}
          </select>
          <select 
            className="update-input" 
            value={selectedAyah} 
            onChange={(e) => setSelectedAyah(e.target.value)}
            style={{flex: 1, background: 'var(--input-bg)', color: 'white', border: '1px solid var(--border)', borderRadius: '8px', padding: '0.5rem'}}
          >
            {ayahOptions}
          </select>
        </div>
        <button onClick={handleSave} style={{width: '100%', background: 'rgba(59, 130, 246, 0.2)', border: '1px solid var(--accent-blue)', color: 'var(--accent-blue)'}}>
          {t('update')}
        </button>
      </div>
      <Link to={`/read/${khatm.id}`} style={{textDecoration: 'none'}}>
        <button className="read-btn">📖 {t('read_quran')}</button>
      </Link>
    </div>
  );
};

// --- GROUP KHATMA COMPONENTS ---

const GroupDashboard = () => {
  const { t } = useTranslation();
  const { token } = useContext(AuthContext);
  const [groupKhatms, setGroupKhatms] = useState([]);
  const [newTitle, setNewTitle] = useState('');

  const fetchGroupKhatms = async () => {
    try {
      const res = await axios.get(`${API_BASE}/group-khatms`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setGroupKhatms(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchGroupKhatms();
  }, []);

  const handleCreateGroup = async (e) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    try {
      await axios.post(`${API_BASE}/group-khatms`,
        { title: newTitle },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setNewTitle('');
      fetchGroupKhatms();
    } catch (err) {
      alert(err.response?.data?.error || 'Error creating group khatma');
    }
  };

  return (
    <div className="container">
      <div className="auth-container" style={{ maxWidth: '100%', margin: '1rem 0', textAlign: 'left' }}>
        <h3>{t('create_group_khatma')}</h3>
        <form onSubmit={handleCreateGroup} style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
          <input
            placeholder={t('group_khatma_title_placeholder')}
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            required
          />
          <button type="submit" style={{ backgroundColor: 'var(--accent-green)' }}>
            {t('create_group_khatma')}
          </button>
        </form>
      </div>

      <h3 className="section-title">👥 {t('group_khatms')}</h3>
      <div className="khatm-grid">
        {groupKhatms.length === 0 ? (
          <p style={{ gridColumn: '1/-1', textAlign: 'center', opacity: 0.6 }}>No group khatmas available yet.</p>
        ) : (
          groupKhatms.map(k => (
            <GroupKhatmCard key={k.id} khatm={k} />
          ))
        )}
      </div>
    </div>
  );
};

const GroupKhmStatusBadge = ({ status, t }) => {
  let color = 'var(--accent-blue)';
  let label = t('open');
  if (status === 'fully_reserved') {
    color = 'var(--accent-yellow)';
    label = t('fully_reserved');
  } else if (status === 'completed') {
    color = 'var(--accent-green)';
    label = t('completed');
  }
  return (
    <span style={{
      backgroundColor: color + '20',
      color: color,
      padding: '0.2rem 0.6rem',
      borderRadius: '20px',
      fontSize: '0.8rem',
      fontWeight: 'bold',
      border: `1px solid ${color}40`
    }}>
      {label}
    </span>
  );
};

const GroupKhatmCard = ({ khatm }) => {
  const { t } = useTranslation();
  const percentage = khatm.overall_progress || 0;

  // Choosing color based on progress
  let barColor = 'blue';
  if (percentage > 50) barColor = 'green';
  if (percentage > 85) barColor = 'yellow';

  return (
    <div className="khatm-card">
      <div className="khatm-card-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: '700' }}>{khatm.title}</h3>
        <GroupKhmStatusBadge status={khatm.status} t={t} />
      </div>

      <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
        <span>Creator: {khatm.creator_name}</span>
      </div>

      <div className="progress-container">
        <div className={`progress-bar ${barColor}`} style={{ width: `${percentage}%` }}></div>
      </div>

      <div className="khatm-info" style={{ marginBottom: '1rem', flexDirection: 'column', gap: '0.4rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
          <span>{t('overall_progress')}:</span>
          <span className="percentage" style={{ fontWeight: 'bold' }}>{percentage}%</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', fontSize: '0.8rem', opacity: 0.8 }}>
          <span>{t('completed_juz_count')}: {khatm.completed_juz_count} / 30</span>
          <span>{t('reserved_juz_count')}: {khatm.reserved_juz_count} / 30</span>
          <span>{t('available_juz_count')}: {khatm.available_juz_count}</span>
        </div>
      </div>

      <Link to={`/group-khatms/${khatm.id}`} style={{ textDecoration: 'none' }}>
        <button style={{ width: '100%', padding: '0.7rem' }}>
          👁️ {t('open')} / {t('reserve')}
        </button>
      </Link>
    </div>
  );
};

const GroupKhatmaDetails = () => {
  const { id } = useParams();
  const { t, i18n } = useTranslation();
  const { token } = useContext(AuthContext);
  const [details, setDetails] = useState(null);
  const [selectedJuz, setSelectedJuz] = useState([]);
  const [isAnonymous, setIsAnonymous] = useState(false);
  const navigate = useNavigate();

  const fetchDetails = async () => {
    try {
      const res = await axios.get(`${API_BASE}/group-khatms/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDetails(res.data);
      setSelectedJuz([]); // Reset selection
    } catch (err) {
      console.error(err);
      alert('Error fetching group khatma details.');
      navigate('/group-khatms');
    }
  };

  useEffect(() => {
    fetchDetails();
  }, [id]);

  const handleJuzClick = (juzNumber, reserved) => {
    if (reserved) return; // Can't select reserved Juz
    if (selectedJuz.includes(juzNumber)) {
      setSelectedJuz(selectedJuz.filter(j => j !== juzNumber));
    } else {
      setSelectedJuz([...selectedJuz, juzNumber]);
    }
  };

  const handleReserve = async () => {
    if (selectedJuz.length === 0) return;
    try {
      await axios.post(`${API_BASE}/group-khatms/${id}/reserve`, {
        juzNumbers: selectedJuz,
        isAnonymous
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchDetails();
    } catch (err) {
      alert(err.response?.data?.error || 'Error reserving Juz.');
    }
  };

  const handleComplete = async (juzNumber) => {
    try {
      await axios.put(`${API_BASE}/group-khatms/${id}/complete`, {
        juzNumber
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchDetails();
    } catch (err) {
      alert(err.response?.data?.error || 'Error completing Juz.');
    }
  };

  if (!details) {
    return (
      <div className="container" style={{ textAlign: 'center', padding: '4rem' }}>
        <div className="spinner" style={{ margin: '0 auto 1rem' }}></div>
        <p>{t('loading_quran')}</p>
      </div>
    );
  }

  return (
    <div className="container">
      {/* Back Button */}
      <Link to="/group-khatms" style={{ textDecoration: 'none' }}>
        <button style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-main)', marginBottom: '1.5rem' }}>
          ⬅️ {t('back_to_dashboard')}
        </button>
      </Link>

      {/* Main Header Info Card */}
      <div className="khatm-card" style={{ marginBottom: '2rem', background: 'var(--card-bg)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.8rem', color: 'var(--accent-blue)', marginBottom: '0.5rem' }}>{details.title}</h2>
            <p style={{ color: 'var(--text-secondary)' }}>👤 {t('creator')}: {details.creator_name}</p>
          </div>
          <GroupKhmStatusBadge status={details.status} t={t} />
        </div>

        <div className="progress-container" style={{ margin: '1.5rem 0' }}>
          <div className="progress-bar green" style={{ width: `${details.overall_progress}%` }}></div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', color: 'var(--text-secondary)' }}>
          <div>
            <strong>{t('overall_progress')}: </strong>
            <span style={{ color: 'var(--accent-green)', fontWeight: 'bold' }}>{details.overall_progress}%</span>
          </div>
          <div style={{ display: 'flex', gap: '1.5rem' }}>
            <span>{t('total_juz')}: 30</span>
            <span>{t('completed_juz_count')}: {details.completed_juz_count}</span>
            <span>{t('reserved_juz_count')}: {details.reserved_juz_count}</span>
            <span>{t('available_juz_count')}: {details.available_juz_count}</span>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '3fr 1fr', gap: '2rem' }} className="details-grid-layout">
        {/* Left Side: Juz Grid & Selection Controls */}
        <div>
          {/* Reserve Box */}
          {details.status !== 'completed' && (
            <div className="khatm-card" style={{ marginBottom: '1.5rem', border: '1px dashed var(--accent-blue)' }}>
              <h4 style={{ marginBottom: '0.8rem' }}>📌 {t('reserve_selected')}</h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                Select available Juz from the grid below to reserve them.
              </p>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', margin: 0 }}>
                  <input
                    type="checkbox"
                    checked={isAnonymous}
                    onChange={(e) => setIsAnonymous(e.target.checked)}
                    style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                  />
                  <span>{t('participate_anonymously')}</span>
                </label>

                <button
                  onClick={handleReserve}
                  disabled={selectedJuz.length === 0}
                  style={{
                    marginLeft: 'auto',
                    backgroundColor: selectedJuz.length > 0 ? 'var(--accent-blue)' : 'var(--input-bg)',
                    color: selectedJuz.length > 0 ? 'white' : 'var(--text-secondary)',
                    cursor: selectedJuz.length > 0 ? 'pointer' : 'not-allowed'
                  }}
                >
                  {t('reserve_selected')} ({selectedJuz.length})
                </button>
              </div>
            </div>
          )}

          {/* 30 Juz Grid */}
          <h3 className="section-title">📖 {t('total_juz')} (30)</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem' }}>
            {details.juz.map(j => {
              const isSelected = selectedJuz.includes(j.juz_number);
              let cardBorder = '1px solid var(--border)';
              let bg = 'var(--card-bg)';
              let badgeColor = 'var(--text-secondary)';
              let badgeLabel = t('available_label');

              if (j.status === 'completed') {
                bg = 'rgba(34, 197, 94, 0.08)';
                cardBorder = '1px solid var(--accent-green)';
                badgeColor = 'var(--accent-green)';
                badgeLabel = t('completed_label');
              } else if (j.reserved) {
                bg = 'rgba(59, 130, 246, 0.05)';
                cardBorder = '1px solid var(--border)';
                badgeColor = 'var(--accent-blue)';
                badgeLabel = t('reserved_label');
              } else if (isSelected) {
                bg = 'rgba(234, 179, 8, 0.05)';
                cardBorder = '2px solid var(--accent-yellow)';
                badgeColor = 'var(--accent-yellow)';
              }

              return (
                <div
                  key={j.juz_number}
                  onClick={() => handleJuzClick(j.juz_number, j.reserved)}
                  style={{
                    background: bg,
                    border: cardBorder,
                    borderRadius: '12px',
                    padding: '1rem',
                    cursor: j.reserved ? 'default' : 'pointer',
                    transition: 'all 0.2s',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    minHeight: '120px'
                  }}
                  className={`juz-grid-card ${isSelected ? 'selected' : ''}`}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{t('juz')} {j.juz_number}</span>
                    <span style={{ fontSize: '0.75rem', color: badgeColor, fontWeight: 'bold' }}>
                      {isSelected && !j.reserved ? '✓ Selected' : badgeLabel}
                    </span>
                  </div>

                  <div style={{ margin: '0.5rem 0 0.8rem 0' }}>
                    {j.reserved ? (
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-main)' }}>
                        <span style={{ opacity: 0.6 }}>{t('reserved_by')}:</span>
                        <div style={{ fontWeight: '600', marginTop: '0.2rem' }}>
                          👤 {j.display_name === 'Anonymous' ? t('anonymous') : j.display_name}
                        </div>
                      </div>
                    ) : (
                      <span style={{ fontSize: '0.8rem', opacity: 0.5 }}>Click to select</span>
                    )}
                  </div>

                  {j.reserved && j.is_owner && (
                    <Link to={`/read-juz/${j.juz_number}?khatmId=${details.id}`} style={{ textDecoration: 'none', width: '100%' }}>
                      <button
                        onClick={(e) => e.stopPropagation()}
                        style={{
                          width: '100%',
                          padding: '0.4rem',
                          fontSize: '0.8rem',
                          backgroundColor: 'var(--accent-blue)',
                          marginBottom: '0.4rem',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '4px'
                        }}
                      >
                        📖 {t('read_juz')}
                      </button>
                    </Link>
                  )}

                  {j.reserved && j.is_owner && j.status === 'reserved' && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation(); // Prevent card selection logic
                        handleComplete(j.juz_number);
                      }}
                      style={{
                        width: '100%',
                        padding: '0.4rem',
                        fontSize: '0.8rem',
                        backgroundColor: 'var(--accent-green)'
                      }}
                    >
                      ✓ {t('mark_as_completed')}
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Side: Participant List */}
        <div>
          <h3 className="section-title">👥 {t('participants')}</h3>
          <div className="khatm-card" style={{ padding: '1rem' }}>
            {details.participants.length === 0 ? (
              <p style={{ opacity: 0.5, fontSize: '0.9rem', textAlign: 'center' }}>No participants yet.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {details.participants.map((p, i) => (
                  <div key={i} style={{ borderBottom: '1px solid var(--border)', paddingBottom: '0.8rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem', fontSize: '0.9rem' }}>
                      <span style={{ fontWeight: 'bold' }}>
                        👤 {p.name === 'Anonymous' ? t('anonymous') : p.name}
                      </span>
                      <span style={{ color: 'var(--accent-blue)', fontWeight: 'bold' }}>{p.progress}%</span>
                    </div>
                    
                    <div className="progress-container" style={{ margin: 0, height: '6px' }}>
                      <div className="progress-bar blue" style={{ width: `${p.progress}%` }}></div>
                    </div>
                    
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', opacity: 0.7, marginTop: '0.3rem' }}>
                      <span>Reserved: {p.reservedCount}</span>
                      <span>Completed: {p.completedCount}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// --- MAIN WRAPPER ---
const AppContent = () => {
  const { token } = useContext(AuthContext);
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/login" element={!token ? <Login /> : <Navigate to="/" />} />
        <Route path="/register" element={!token ? <Register /> : <Navigate to="/" />} />
        <Route path="/" element={token ? <Dashboard /> : <Navigate to="/login" />} />
        <Route path="/read/:khatmId" element={token ? <QuranReader /> : <Navigate to="/login" />} />
        <Route path="/read-juz/:juzNum" element={token ? <JuzReader /> : <Navigate to="/login" />} />
        <Route path="/group-khatms" element={token ? <GroupDashboard /> : <Navigate to="/login" />} />
        <Route path="/group-khatms/:id" element={token ? <GroupKhatmaDetails /> : <Navigate to="/login" />} />
      </Routes>
    </>
  );
};

const App = () => (
  <AuthProvider>
    <Router>
      <AppContent />
    </Router>
  </AuthProvider>
);

export default App;
