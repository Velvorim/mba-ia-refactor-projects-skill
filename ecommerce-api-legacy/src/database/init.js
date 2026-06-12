/**
 * database/init.js
 * Inicializa o esquema e dados de seed do banco SQLite em memória.
 * Chamado uma única vez no startup da aplicação.
 */
const { db, dbRun } = require('./index');

function initDb() {
  return new Promise((resolve, reject) => {
    db.serialize(() => {
      db.run('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)');
      db.run('CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)');
      db.run('CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)');
      db.run('CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)');
      db.run('CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');

      // Seed de dados de exemplo
      db.run("INSERT INTO users (name, email, pass) VALUES ('Leonan', 'leonan@fullcycle.com.br', '123')");
      db.run("INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)");
      db.run("INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)");
      db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')", [], function (err) {
        if (err) return reject(err);
        resolve();
      });
    });
  });
}

module.exports = { initDb };
