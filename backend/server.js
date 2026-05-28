const express = require('express');
const cors = require('cors');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
require('dotenv').config();
const db = require('./db');
const adminRoute = require('./routes/admin');

const app = express();
const PORT = process.env.PORT || 5000;
const SECRET = process.env.JWT_SECRET || 'supersecretkey';

app.use(cors());
app.use(express.json());
app.use('/admin', adminRoute);

// Authentication Middleware
const authenticate = (req, res, next) => {
  const token = req.headers['authorization'];
  if (!token) return res.status(401).json({ error: 'Unauthorized' });

  jwt.verify(token.split(' ')[1], SECRET, (err, decoded) => {
    if (err) return res.status(403).json({ error: 'Forbidden' });
    req.userId = decoded.id;
    next();
  });
};

// Register API
app.post('/api/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!name || !email || !password) return res.status(400).json({ error: 'Missing fields' });

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    const sql = `INSERT INTO users (name, email, password) VALUES (?, ?, ?)`;
    db.run(sql, [name, email, hashedPassword], function (err) {
      if (err) {
        if (err.message.includes('UNIQUE')) return res.status(400).json({ error: 'Email already exists' });
        return res.status(500).json({ error: err.message });
      }
      res.status(201).json({ message: 'User registered successfully' });
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Login API
app.post('/api/auth/login', (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'Missing fields' });

  db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, user) => {
    if (err) return res.status(500).json({ error: err.message });
    if (!user) return res.status(400).json({ error: 'Invalid credentials' });

    const match = await bcrypt.compare(password, user.password);
    if (!match) return res.status(400).json({ error: 'Invalid credentials' });

    const token = jwt.sign({ id: user.id }, SECRET, { expiresIn: '1d' });
    res.json({ token, user: { id: user.id, name: user.name, email: user.email } });
  });
});

// Get User Khatms API
app.get('/api/khatms', authenticate, (req, res) => {
  db.all(`SELECT * FROM khatms WHERE owner_id = ?`, [req.userId], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

// Create Khatm API
app.post('/api/khatms', authenticate, (req, res) => {
  const { title, target_person, type } = req.body;
  const sql = `INSERT INTO khatms (title, owner_id, target_person, type) VALUES (?, ?, ?, ?)`;
  db.run(sql, [title, req.userId, target_person, type || 'self'], function (err) {
    if (err) {
      console.error('Error creating khatm:', err);
      return res.status(500).json({ error: err.message });
    }
    res.json({ id: this.lastID, title, owner_id: req.userId, target_person, type });
  });
});

// Update Progress API
app.put('/api/khatms/:id', authenticate, (req, res) => {
  const { last_ayah } = req.body;
  const sql = `UPDATE khatms SET last_ayah = ? WHERE id = ? AND owner_id = ?`;
  db.run(sql, [last_ayah, req.params.id, req.userId], function (err) {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ message: 'Progress updated' });
  });
});

// Delete Khatm API
app.delete('/api/khatms/:id', authenticate, (req, res) => {
  const sql = `DELETE FROM khatms WHERE id = ? AND owner_id = ?`;
  db.run(sql, [req.params.id, req.userId], function (err) {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ message: 'Khatm deleted' });
  });
});

// --- GROUP KHATMA APIs ---

// 1. Create Group Khatma
app.post('/api/group-khatms', authenticate, (req, res) => {
  const { title } = req.body;
  if (!title) return res.status(400).json({ error: 'Missing title' });

  const sql = `INSERT INTO group_khatms (title, creator_id) VALUES (?, ?)`;
  db.run(sql, [title, req.userId], function (err) {
    if (err) {
      console.error('Error creating group khatm:', err);
      return res.status(500).json({ error: err.message });
    }
    res.status(201).json({
      id: this.lastID,
      title,
      creator_id: req.userId,
      status: 'open'
    });
  });
});

// 2. Get All Group Khatmas
app.get('/api/group-khatms', authenticate, (req, res) => {
  const sql = `
    SELECT 
      g.id, g.title, g.creator_id, g.status, g.created_at, g.updated_at,
      u.name as creator_name,
      COUNT(r.id) as reserved_juz_count,
      COALESCE(SUM(CASE WHEN r.status = 'completed' THEN 1 ELSE 0 END), 0) as completed_juz_count
    FROM group_khatms g
    JOIN users u ON g.creator_id = u.id
    LEFT JOIN group_khatm_reservations r ON g.id = r.group_khatma_id
    GROUP BY g.id
    ORDER BY g.created_at DESC
  `;
  db.all(sql, [], (err, rows) => {
    if (err) {
      console.error('Error fetching group khatms:', err);
      return res.status(500).json({ error: err.message });
    }
    const result = rows.map(row => {
      const reserved = row.reserved_juz_count;
      const completed = row.completed_juz_count;
      const available = 30 - reserved;
      const progress = Math.round((completed / 30) * 100);
      return {
        id: row.id,
        title: row.title,
        creator_id: row.creator_id,
        creator_name: row.creator_name,
        status: row.status,
        created_at: row.created_at,
        updated_at: row.updated_at,
        total_juz: 30,
        reserved_juz_count: reserved,
        available_juz_count: available,
        completed_juz_count: completed,
        overall_progress: progress
      };
    });
    res.json(result);
  });
});

// 3. Get Single Group Khatma Details
app.get('/api/group-khatms/:id', authenticate, (req, res) => {
  const khatmaId = req.params.id;

  // Get metadata
  const khatmaSql = `
    SELECT g.id, g.title, g.creator_id, g.status, g.created_at, g.updated_at, u.name as creator_name
    FROM group_khatms g
    JOIN users u ON g.creator_id = u.id
    WHERE g.id = ?
  `;

  db.get(khatmaSql, [khatmaId], (err, khatma) => {
    if (err) return res.status(500).json({ error: err.message });
    if (!khatma) return res.status(404).json({ error: 'Group Khatma not found' });

    // Get reservations
    const resSql = `
      SELECT r.id, r.juz_number, r.user_id, r.display_name, r.is_anonymous, r.status, r.completed_at, u.name as user_name
      FROM group_khatm_reservations r
      JOIN users u ON r.user_id = u.id
      WHERE r.group_khatma_id = ?
    `;

    db.all(resSql, [khatmaId], (err, reservations) => {
      if (err) return res.status(500).json({ error: err.message });

      // Construct 30 Juz details
      const juzList = [];
      let completed_count = 0;
      let reserved_count = 0;

      for (let j = 1; j <= 30; j++) {
        const resObj = reservations.find(r => r.juz_number === j);
        if (resObj) {
          reserved_count++;
          if (resObj.status === 'completed') {
            completed_count++;
          }
          juzList.push({
            juz_number: j,
            reserved: true,
            status: resObj.status,
            display_name: resObj.is_anonymous ? 'Anonymous' : resObj.display_name,
            is_anonymous: !!resObj.is_anonymous,
            is_owner: resObj.user_id === req.userId,
            user_id: resObj.user_id,
            completed_at: resObj.completed_at
          });
        } else {
          juzList.push({
            juz_number: j,
            reserved: false,
            status: 'available',
            display_name: null,
            is_anonymous: false,
            is_owner: false,
            user_id: null,
            completed_at: null
          });
        }
      }

      // Compute participant progress
      const participantsMap = {};
      reservations.forEach(r => {
        const key = r.is_anonymous ? `anon_${r.user_id}` : `pub_${r.user_id}`;
        if (!participantsMap[key]) {
          participantsMap[key] = {
            name: r.is_anonymous ? 'Anonymous' : r.display_name,
            is_anonymous: !!r.is_anonymous,
            reservedCount: 0,
            completedCount: 0
          };
        }
        participantsMap[key].reservedCount++;
        if (r.status === 'completed') {
          participantsMap[key].completedCount++;
        }
      });

      const participants = Object.values(participantsMap).map(p => ({
        ...p,
        progress: Math.round((p.completedCount / p.reservedCount) * 100)
      }));

      const available_count = 30 - reserved_count;
      const overall_progress = Math.round((completed_count / 30) * 100);

      res.json({
        id: khatma.id,
        title: khatma.title,
        creator_id: khatma.creator_id,
        creator_name: khatma.creator_name,
        status: khatma.status,
        created_at: khatma.created_at,
        updated_at: khatma.updated_at,
        total_juz: 30,
        reserved_juz_count: reserved_count,
        available_juz_count: available_count,
        completed_juz_count: completed_count,
        overall_progress,
        juz: juzList,
        participants
      });
    });
  });
});

// 4. Reserve Juz
app.post('/api/group-khatms/:id/reserve', authenticate, (req, res) => {
  const khatmaId = req.params.id;
  const { juzNumbers, isAnonymous } = req.body;

  if (!Array.isArray(juzNumbers) || juzNumbers.length === 0) {
    return res.status(400).json({ error: 'Please select at least one Juz.' });
  }

  // Validate Juz numbers
  const invalidJuz = juzNumbers.find(j => j < 1 || j > 30);
  if (invalidJuz !== undefined) {
    return res.status(400).json({ error: 'Invalid Juz number. Must be between 1 and 30.' });
  }

  // Check if group khatma exists
  db.get(`SELECT status FROM group_khatms WHERE id = ?`, [khatmaId], (err, gKhatm) => {
    if (err) return res.status(500).json({ error: err.message });
    if (!gKhatm) return res.status(404).json({ error: 'Group Khatma not found' });
    if (gKhatm.status === 'completed') {
      return res.status(400).json({ error: 'This Group Khatma is already completed.' });
    }

    // Check if any of requested Juz are already reserved
    const placeholders = juzNumbers.map(() => '?').join(',');
    const checkSql = `SELECT juz_number FROM group_khatm_reservations WHERE group_khatma_id = ? AND juz_number IN (${placeholders})`;
    
    db.all(checkSql, [khatmaId, ...juzNumbers], (err, rows) => {
      if (err) return res.status(500).json({ error: err.message });
      if (rows.length > 0) {
        const alreadyReserved = rows.map(r => r.juz_number).join(', ');
        return res.status(400).json({ error: `Juz ${alreadyReserved} already reserved.` });
      }

      // Fetch user name
      db.get(`SELECT name FROM users WHERE id = ?`, [req.userId], (err, user) => {
        if (err) return res.status(500).json({ error: err.message });
        if (!user) return res.status(404).json({ error: 'User not found' });

        const displayName = isAnonymous ? 'Anonymous' : user.name;

        // Perform inserts
        db.serialize(() => {
          const insertSql = `INSERT INTO group_khatm_reservations (group_khatma_id, juz_number, user_id, display_name, is_anonymous) VALUES (?, ?, ?, ?, ?)`;
          const stmt = db.prepare(insertSql);
          
          let insertErr = null;
          juzNumbers.forEach(juz => {
            stmt.run([khatmaId, juz, req.userId, displayName, isAnonymous ? 1 : 0], (err) => {
              if (err) insertErr = err;
            });
          });

          stmt.finalize((err) => {
            if (err || insertErr) {
              console.error('Insert error:', err || insertErr);
              return res.status(500).json({ error: (err || insertErr).message });
            }

            // Check if all 30 Juz are now reserved to update Group Khatma status
            db.get(`SELECT COUNT(*) as count FROM group_khatm_reservations WHERE group_khatma_id = ?`, [khatmaId], (err, row) => {
              if (row && row.count === 30) {
                db.run(`UPDATE group_khatms SET status = 'fully_reserved', updated_at = CURRENT_TIMESTAMP WHERE id = ?`, [khatmaId], () => {
                  res.json({ message: 'Reservation successful!' });
                });
              } else {
                res.json({ message: 'Reservation successful!' });
              }
            });
          });
        });
      });
    });
  });
});

// 5. Complete Juz
app.put('/api/group-khatms/:id/complete', authenticate, (req, res) => {
  const khatmaId = req.params.id;
  const { juzNumber } = req.body;

  if (!juzNumber) return res.status(400).json({ error: 'Missing Juz number.' });

  const updateSql = `
    UPDATE group_khatm_reservations 
    SET status = 'completed', completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
    WHERE group_khatma_id = ? AND juz_number = ? AND user_id = ? AND status = 'reserved'
  `;

  db.run(updateSql, [khatmaId, juzNumber, req.userId], function (err) {
    if (err) return res.status(500).json({ error: err.message });
    if (this.changes === 0) {
      return res.status(400).json({ error: 'Cannot complete this Juz. Either it is not reserved by you, or it is already completed.' });
    }

    // Check if all 30 Juz are completed for this Group Khatma
    db.get(`
      SELECT COUNT(*) as count 
      FROM group_khatm_reservations 
      WHERE group_khatma_id = ? AND status = 'completed'
    `, [khatmaId], (err, row) => {
      if (row && row.count === 30) {
        db.run(`UPDATE group_khatms SET status = 'completed', updated_at = CURRENT_TIMESTAMP WHERE id = ?`, [khatmaId], () => {
          res.json({ message: 'Juz marked as completed. Group Khatma is now fully completed!' });
        });
      } else {
        res.json({ message: 'Juz marked as completed.' });
      }
    });
  });
});

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
