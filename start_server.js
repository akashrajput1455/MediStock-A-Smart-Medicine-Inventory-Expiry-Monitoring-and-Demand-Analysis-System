import { spawn } from 'child_process';

// Parse arguments passed by npm / AI Studio supervisor (e.g. --port 3000 --host 0.0.0.0)
const args = process.argv.slice(2);
let port = '3000';
let host = '0.0.0.0';

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--port' && args[i + 1]) {
    port = args[i + 1];
    i++;
  } else if (args[i].startsWith('--port=')) {
    port = args[i].split('=')[1];
  } else if (args[i] === '--host' && args[i + 1]) {
    host = args[i + 1];
    i++;
  } else if (args[i].startsWith('--host=')) {
    host = args[i].split('=')[1];
  }
}

const streamlitArgs = [
  'run',
  'app.py',
  '--server.port',
  port,
  '--server.address',
  host,
  '--server.headless',
  'true',
  '--server.enableCORS',
  'false',
  '--server.enableXsrfProtection',
  'false',
  '--browser.gatherUsageStats',
  'false',
];

console.log(`[MediStock Runner] Launching Streamlit on http://${host}:${port}`);
const proc = spawn('streamlit', streamlitArgs, {
  stdio: 'inherit',
});

proc.on('error', (err) => {
  console.error('[MediStock Runner Error]', err);
  process.exit(1);
});

proc.on('exit', (code, signal) => {
  console.log(`[MediStock Runner] Streamlit exited with code ${code} signal ${signal}`);
  process.exit(code || 0);
});

process.on('SIGINT', () => {
  proc.kill('SIGINT');
  process.exit(0);
});

process.on('SIGTERM', () => {
  proc.kill('SIGTERM');
  process.exit(0);
});
