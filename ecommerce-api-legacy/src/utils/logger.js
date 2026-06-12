/**
 * utils/logger.js
 * PT-06: Logger estruturado em JSON — substitui todos os console.log() de produção.
 * Emite para stdout/stderr com timestamp, nível e metadata.
 *
 * Para produção, considere substituir por winston ou pino:
 *   npm install pino
 */

function log(level, msg, meta = {}) {
  const entry = JSON.stringify({
    ts:    new Date().toISOString(),
    level,
    msg,
    ...meta,
  });
  if (level === 'error') {
    process.stderr.write(entry + '\n');
  } else {
    process.stdout.write(entry + '\n');
  }
}

const logger = {
  info:  (msg, meta) => log('info',  msg, meta),
  warn:  (msg, meta) => log('warn',  msg, meta),
  error: (msg, meta) => log('error', msg, meta),
  debug: (msg, meta) => log('debug', msg, meta),
};

module.exports = logger;
