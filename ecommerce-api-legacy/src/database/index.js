/**
 * database/index.js
 * PT-08: Cria a instância SQLite uma única vez e expõe Promise wrappers (dbGet, dbAll, dbRun).
 * Elimina callback hell em toda a aplicação.
 */
const sqlite3  = require('sqlite3').verbose();
const settings = require('../config/settings');

const db = new sqlite3.Database(settings.dbPath);

/** Executa uma query que retorna zero ou uma linha. */
function dbGet(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
  });
}

/** Executa uma query que retorna múltiplas linhas. */
function dbAll(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
  });
}

/** Executa INSERT / UPDATE / DELETE; resolve com { lastID, changes }. */
function dbRun(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function (err) {
      if (err) return reject(err);
      resolve({ lastID: this.lastID, changes: this.changes });
    });
  });
}

/** Executa uma série de comandos serializados (usado em initDb). */
function serialize(fn) {
  return new Promise((resolve) => {
    db.serialize(() => {
      fn();
      resolve();
    });
  });
}

module.exports = { db, dbGet, dbAll, dbRun, serialize };
