const express = require('express');
const router = express.Router();
const db = require('../db');

router.get('/', (req, res) => {
  db.all(`
    SELECT 
      u.id as user_id, u.name, u.email,
      k.id as khatm_id, k.title, k.target_person, k.type, k.last_ayah, k.total_ayahs
    FROM users u
    LEFT JOIN khatms k ON u.id = k.owner_id
    ORDER BY u.id
  `, (err, rows) => {
    if (err) return res.status(500).send('Database error: ' + err.message);

    // Group by user
    const usersMap = {};
    rows.forEach(row => {
      if (!usersMap[row.user_id]) {
        usersMap[row.user_id] = {
          id: row.user_id,
          name: row.name,
          email: row.email,
          khatms: []
        };
      }
      if (row.khatm_id) {
        usersMap[row.user_id].khatms.push({
          id: row.khatm_id,
          title: row.title,
          target_person: row.target_person,
          type: row.type,
          last_ayah: row.last_ayah,
          total_ayahs: row.total_ayahs,
          percent: Math.round((row.last_ayah / 6236) * 100)
        });
      }
    });

    const users = Object.values(usersMap);

    const html = `
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hayırhah - لوحة قاعدة البيانات</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      padding: 2rem;
      min-height: 100vh;
    }
    .header {
      text-align: center;
      margin-bottom: 2.5rem;
    }
    .header h1 {
      font-size: 2rem;
      color: #3b82f6;
      margin-bottom: 0.5rem;
    }
    .header p {
      color: #64748b;
      font-size: 0.95rem;
    }
    .stats {
      display: flex;
      gap: 1.5rem;
      justify-content: center;
      margin-bottom: 2.5rem;
      flex-wrap: wrap;
    }
    .stat-card {
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 1.2rem 2rem;
      text-align: center;
      min-width: 150px;
    }
    .stat-card .number {
      font-size: 2.2rem;
      font-weight: 700;
      color: #3b82f6;
    }
    .stat-card .label {
      font-size: 0.85rem;
      color: #64748b;
      margin-top: 0.3rem;
    }
    .user-card {
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 16px;
      margin-bottom: 1.5rem;
      overflow: hidden;
    }
    .user-header {
      background: linear-gradient(135deg, #1d4ed8, #1e40af);
      padding: 1rem 1.5rem;
      display: flex;
      align-items: center;
      gap: 1rem;
    }
    .user-avatar {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: rgba(255,255,255,0.2);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.4rem;
      font-weight: 700;
    }
    .user-info h2 { font-size: 1.1rem; font-weight: 700; }
    .user-info p { font-size: 0.85rem; opacity: 0.8; }
    .badge {
      margin-right: auto;
      background: rgba(255,255,255,0.15);
      padding: 0.3rem 0.8rem;
      border-radius: 999px;
      font-size: 0.8rem;
    }
    .khatms-section { padding: 1.5rem; }
    .khatms-section h3 {
      color: #94a3b8;
      font-size: 0.85rem;
      font-weight: 600;
      margin-bottom: 1rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .no-khatms {
      color: #475569;
      font-style: italic;
      text-align: center;
      padding: 1rem;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
    }
    th {
      background: #0f172a;
      color: #64748b;
      padding: 0.7rem 1rem;
      text-align: right;
      font-weight: 600;
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    td {
      padding: 0.8rem 1rem;
      border-top: 1px solid #1e293b;
      color: #cbd5e1;
    }
    tr:hover td { background: rgba(59,130,246,0.05); }
    .progress-bar {
      height: 8px;
      background: #0f172a;
      border-radius: 999px;
      overflow: hidden;
      min-width: 100px;
    }
    .progress-fill {
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, #3b82f6, #06b6d4);
    }
    .type-badge {
      display: inline-block;
      padding: 0.2rem 0.6rem;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 600;
    }
    .type-self { background: rgba(34,197,94,0.15); color: #4ade80; }
    .type-other { background: rgba(168,85,247,0.15); color: #c084fc; }
    .footer {
      text-align: center;
      margin-top: 3rem;
      color: #334155;
      font-size: 0.85rem;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>🕌 Hayırhah</h1>
    <p>لوحة عرض بيانات قاعدة البيانات - Database Dashboard</p>
  </div>

  <div class="stats">
    <div class="stat-card">
      <div class="number">${users.length}</div>
      <div class="label">إجمالي المستخدمين<br>Kayıtlı Kullanıcı</div>
    </div>
    <div class="stat-card">
      <div class="number">${rows.filter(r => r.khatm_id).length}</div>
      <div class="label">إجمالي الختمات<br>Toplam Hatım</div>
    </div>
    <div class="stat-card">
      <div class="number">${rows.filter(r => r.type === 'self').length}</div>
      <div class="label">ختمات شخصية<br>Kişisel Hatım</div>
    </div>
    <div class="stat-card">
      <div class="number">${rows.filter(r => r.type === 'other').length}</div>
      <div class="label">ختمات إهداء<br>Hediye Hatım</div>
    </div>
  </div>

  ${users.map(user => `
  <div class="user-card">
    <div class="user-header">
      <div class="user-avatar">${user.name.charAt(0).toUpperCase()}</div>
      <div class="user-info">
        <h2>${user.name}</h2>
        <p>${user.email}</p>
      </div>
      <span class="badge">ID: ${user.id} | ${user.khatms.length} ختمة</span>
    </div>
    <div class="khatms-section">
      <h3>الختمات المسجلة - Hatımlar</h3>
      ${user.khatms.length === 0 ? '<p class="no-khatms">لا توجد ختمات مسجلة بعد - Henüz hatım yok</p>' : `
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>العنوان / Başlık</th>
            <th>لمن / Kişi</th>
            <th>النوع / Tür</th>
            <th>التقدم / İlerleme</th>
            <th>آية / Ayet</th>
          </tr>
        </thead>
        <tbody>
          ${user.khatms.map(k => `
          <tr>
            <td>${k.id}</td>
            <td>${k.title || '-'}</td>
            <td>${k.target_person || '-'}</td>
            <td><span class="type-badge type-${k.type}">${k.type === 'self' ? 'شخصي' : 'إهداء'}</span></td>
            <td>
              <div style="display:flex;align-items:center;gap:0.5rem">
                <div class="progress-bar">
                  <div class="progress-fill" style="width:${k.percent}%"></div>
                </div>
                <span style="font-size:0.8rem;color:#64748b">${k.percent}%</span>
              </div>
            </td>
            <td style="font-family:monospace">${k.last_ayah} / ${k.total_ayahs}</td>
          </tr>
          `).join('')}
        </tbody>
      </table>
      `}
    </div>
  </div>
  `).join('')}

  <div class="footer">
    <p>🕐 تم توليد هذه الصفحة في: ${new Date().toLocaleString('ar-EG')}</p>
    <p style="margin-top:0.5rem">Hayırhah - Quran Khatm Tracker | Backend: Node.js + Express + SQLite</p>
  </div>
</body>
</html>`;

    res.send(html);
  });
});

module.exports = router;
