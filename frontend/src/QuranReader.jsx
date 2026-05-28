import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { surahs, getAyahIndex, getSurahFromIndex } from './surahData';

const API_BASE = 'http://localhost:5000/api';

// We need AuthContext from App — export it there and import here
// For now we read token from localStorage directly
const QuranReader = () => {
  const { khatmId } = useParams();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const currentLang = i18n.language;
  const token = localStorage.getItem('token');

  const [khatm, setKhatm] = useState(null);
  const [selectedSurahId, setSelectedSurahId] = useState(1);
  const [ayahs, setAyahs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [confirmAyah, setConfirmAyah] = useState(null); // for confirmation dialog

  // Fetch khatm details to know where user left off
  useEffect(() => {
    const fetchKhatm = async () => {
      try {
        const res = await axios.get(`${API_BASE}/khatms`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const found = res.data.find(k => k.id === parseInt(khatmId));
        if (found) {
          setKhatm(found);
          const { surah } = getSurahFromIndex(found.last_ayah);
          setSelectedSurahId(surah.id);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchKhatm();
  }, [khatmId]);

  // Fetch ayahs from Alquran Cloud API when surah changes
  useEffect(() => {
    const fetchAyahs = async () => {
      setLoading(true);
      try {
        const res = await fetch(`https://api.alquran.cloud/v1/surah/${selectedSurahId}/quran-uthmani`);
        const data = await res.json();
        if (data.code === 200) {
          setAyahs(data.data.ayahs);
        }
      } catch (err) {
        console.error('Error fetching Quran data:', err);
      }
      setLoading(false);
    };
    fetchAyahs();
  }, [selectedSurahId]);

  const handleAyahClick = (ayahNumberInSurah) => {
    setConfirmAyah(ayahNumberInSurah);
  };

  const handleConfirmSave = async () => {
    if (!confirmAyah) return;
    const globalIndex = getAyahIndex(selectedSurahId, confirmAyah);
    try {
      await axios.put(`${API_BASE}/khatms/${khatmId}`,
        { last_ayah: globalIndex },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Refresh khatm data
      const res = await axios.get(`${API_BASE}/khatms`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const found = res.data.find(k => k.id === parseInt(khatmId));
      if (found) setKhatm(found);
      setConfirmAyah(null);
    } catch (err) {
      console.error(err);
    }
  };

  const currentSurah = surahs.find(s => s.id === selectedSurahId);
  const percentage = khatm ? Math.round((khatm.last_ayah / 6236) * 100) : 0;
  const lastAyahInfo = khatm ? getSurahFromIndex(khatm.last_ayah) : null;

  // Determine if an ayah has been "read" (is before or equal to last_ayah)
  const isAyahRead = (ayahNumberInSurah) => {
    if (!khatm) return false;
    const globalIndex = getAyahIndex(selectedSurahId, ayahNumberInSurah);
    return globalIndex <= khatm.last_ayah;
  };

  return (
    <div className="quran-reader-page">
      {/* Top Bar */}
      <div className="reader-topbar">
        <button className="back-btn" onClick={() => navigate('/')}>
          ← {t('back_to_dashboard')}
        </button>
        <div className="reader-progress-info">
          <span className="reader-khatm-title">{khatm?.title || '...'}</span>
          <span className="reader-percentage">{percentage}%</span>
        </div>
      </div>

      {/* Surah Selector */}
      <div className="surah-selector">
        <div className="surah-nav">
          <button
            className="surah-nav-btn"
            disabled={selectedSurahId <= 1}
            onClick={() => setSelectedSurahId(prev => Math.max(1, prev - 1))}
          >
            {currentLang === 'ar' ? '→' : '←'}
          </button>

          <select
            className="surah-select"
            value={selectedSurahId}
            onChange={(e) => setSelectedSurahId(parseInt(e.target.value))}
          >
            {surahs.map(s => (
              <option key={s.id} value={s.id}>
                {s.id}. {currentLang === 'ar' ? s.name : s.nameTr}
              </option>
            ))}
          </select>

          <button
            className="surah-nav-btn"
            disabled={selectedSurahId >= 114}
            onClick={() => setSelectedSurahId(prev => Math.min(114, prev + 1))}
          >
            {currentLang === 'ar' ? '←' : '→'}
          </button>
        </div>

        <div className="surah-info-bar">
          <span>{currentLang === 'ar' ? currentSurah?.name : currentSurah?.nameTr}</span>
          <span className="ayah-count">{currentSurah?.ayahs} {t('ayahs_count')}</span>
        </div>
      </div>

      {/* Quran Text Area */}
      <div className="quran-text-container">
        {/* Bismillah - except for Surah 9 (At-Tawbah) and Surah 1 (Al-Fatiha has it as first ayah) */}
        {selectedSurahId !== 9 && selectedSurahId !== 1 && (
          <div className="bismillah">بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ</div>
        )}

        {loading ? (
          <div className="quran-loading">
            <div className="spinner"></div>
            <p>{t('loading_quran')}</p>
          </div>
        ) : (
          <div className="ayahs-container" dir="rtl">
            {ayahs.map((ayah) => {
              const ayahNum = ayah.numberInSurah;
              const read = isAyahRead(ayahNum);
              return (
                <span
                  key={ayah.number}
                  className={`ayah-text ${read ? 'ayah-read' : ''} ${confirmAyah === ayahNum ? 'ayah-selected' : ''}`}
                  onClick={() => handleAyahClick(ayahNum)}
                  title={`${t('ayah')} ${ayahNum}`}
                >
                  {ayah.text}
                  <span className="ayah-number">﴿{ayahNum}﴾</span>
                </span>
              );
            })}
          </div>
        )}
      </div>

      {/* Confirmation Dialog */}
      {confirmAyah !== null && (
        <div className="confirm-overlay" onClick={() => setConfirmAyah(null)}>
          <div className="confirm-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="confirm-icon">📖</div>
            <h3>{t('confirm_save_title')}</h3>
            <p>
              {t('confirm_save_message', {
                surah: currentLang === 'ar' ? currentSurah?.name : currentSurah?.nameTr,
                ayah: confirmAyah
              })}
            </p>
            <div className="confirm-actions">
              <button className="confirm-yes" onClick={handleConfirmSave}>
                ✓ {t('confirm_yes')}
              </button>
              <button className="confirm-no" onClick={() => setConfirmAyah(null)}>
                ✕ {t('confirm_no')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuranReader;
