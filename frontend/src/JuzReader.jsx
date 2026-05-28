import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const JuzReader = () => {
  const { juzNum } = useParams();
  const [searchParams] = useSearchParams();
  const khatmId = searchParams.get('khatmId');
  const navigate = useNavigate();
  const { t } = useTranslation();

  const [ayahs, setAyahs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchJuzAyahs = async () => {
      setLoading(true);
      try {
        const res = await fetch(`https://api.alquran.cloud/v1/juz/${juzNum}/quran-uthmani`);
        const data = await res.json();
        if (data.code === 200) {
          setAyahs(data.data.ayahs);
        }
      } catch (err) {
        console.error('Error fetching Juz data:', err);
      }
      setLoading(false);
    };
    fetchJuzAyahs();
  }, [juzNum]);

  const backPath = khatmId ? `/group-khatms/${khatmId}` : '/group-khatms';

  return (
    <div className="quran-reader-page">
      {/* Top Bar */}
      <div className="reader-topbar">
        <button className="back-btn" onClick={() => navigate(backPath)}>
          ← {t('back_to_dashboard')}
        </button>
        <div className="reader-progress-info">
          <span className="reader-percentage" style={{ background: 'rgba(59,130,246,0.15)', color: 'var(--accent-blue)', padding: '0.3rem 0.8rem', borderRadius: '20px', fontWeight: 'bold' }}>
            {t('juz')} {juzNum}
          </span>
        </div>
      </div>

      {/* Quran Text Area */}
      <div className="quran-text-container" style={{ padding: '2rem', maxWidth: '900px', margin: '0 auto', width: '100%' }}>
        {loading ? (
          <div className="quran-loading" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem', gap: '1rem', color: 'var(--text-secondary)' }}>
            <div className="spinner"></div>
            <p>{t('loading_quran')}</p>
          </div>
        ) : (
          <div className="ayahs-container" dir="rtl" style={{ fontFamily: "'Amiri', serif", fontSize: '1.65rem', lineHeight: '2.8', textAlign: 'justify', direction: 'rtl', color: 'var(--text-main)' }}>
            {ayahs.map((ayah, index) => {
              const showSurahHeader = index === 0 || ayahs[index - 1].surah.number !== ayah.surah.number;
              const showBismillah = showSurahHeader && ayah.surah.number !== 9 && ayah.surah.number !== 1 && ayah.numberInSurah === 1;

              return (
                <React.Fragment key={ayah.number}>
                  {showSurahHeader && (
                    <div style={{
                      textAlign: 'center',
                      color: 'var(--accent-blue)',
                      fontSize: '1.8rem',
                      fontWeight: 'bold',
                      margin: '2rem 0 1rem',
                      borderBottom: '1px solid var(--border)',
                      paddingBottom: '0.5rem'
                    }}>
                      سُورَةُ {ayah.surah.name.replace('سُورَةُ', '').trim()}
                    </div>
                  )}
                  {showBismillah && (
                    <div className="bismillah" style={{
                      textAlign: 'center',
                      fontFamily: "'Amiri', serif",
                      fontSize: '1.8rem',
                      color: 'var(--accent-yellow)',
                      padding: '1rem 0',
                      marginBottom: '1rem'
                    }}>
                      بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ
                    </div>
                  )}
                  <span
                    className="ayah-text"
                    title={`${t('ayah')} ${ayah.numberInSurah}`}
                    style={{
                      cursor: 'default',
                      padding: '2px 4px',
                      borderRadius: '4px',
                      transition: 'background 0.2s',
                      position: 'relative'
                    }}
                  >
                    {ayah.numberInSurah === 1 && ayah.surah.number !== 1 && ayah.text.startsWith('بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ ') 
                      ? ayah.text.replace('بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ ', '') 
                      : ayah.text}
                    <span className="ayah-number" style={{ fontSize: '0.9rem', color: 'var(--accent-blue)', margin: '0 6px', fontFamily: "'Outfit', sans-serif" }}>
                      ﴿{ayah.numberInSurah}﴾
                    </span>
                  </span>
                </React.Fragment>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default JuzReader;
