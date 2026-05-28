const sqlite3 = require('sqlite3').verbose();
const path = require('path');
require('dotenv').config();

const dbPath = path.resolve(__dirname, process.env.DB_FILE || 'database.sqlite');
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Database connection error:', err.message);
  } else {
    console.log('Connected to SQLite database.');
  }
});

// Initialize tables
db.serialize(() => {
  // Users table
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
  )`);

  // Khatms table
  db.run(`CREATE TABLE IF NOT EXISTS khatms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    owner_id INTEGER NOT NULL,
    target_person TEXT,
    last_ayah INTEGER DEFAULT 0,
    total_ayahs INTEGER DEFAULT 6236,
    type TEXT CHECK(type IN ('self', 'other')) DEFAULT 'self',
    FOREIGN KEY (owner_id) REFERENCES users (id)
  )`);

  // Group Khatms table
  db.run(`CREATE TABLE IF NOT EXISTS group_khatms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    creator_id INTEGER NOT NULL,
    status TEXT CHECK(status IN ('open', 'fully_reserved', 'completed')) DEFAULT 'open',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users (id)
  )`);

  // Group Khatm Juz Reservations table
  db.run(`CREATE TABLE IF NOT EXISTS group_khatm_reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_khatma_id INTEGER NOT NULL,
    juz_number INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    display_name TEXT NOT NULL,
    is_anonymous INTEGER DEFAULT 0,
    status TEXT CHECK(status IN ('reserved', 'completed')) DEFAULT 'reserved',
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_khatma_id) REFERENCES group_khatms (id),
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE (group_khatma_id, juz_number)
  )`);
});

module.exports = db;
