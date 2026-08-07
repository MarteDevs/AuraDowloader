// Cross-platform wrapper for the favicon generator.
// Lets `npm run build` regenerate the favicon from aura-logo.png on every build.
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const script = resolve(here, 'build_favicon.py');

if (!existsSync(script)) {
  console.error(`[favicon] script not found: ${script}`);
  process.exit(1);
}

const py = process.platform === 'win32' ? 'py' : 'python3';
const child = spawn(py, [script], { stdio: 'inherit', shell: false });

child.on('exit', (code) => {
  if (code !== 0) {
    console.error(`[favicon] generator exited with code ${code}`);
    process.exit(code ?? 1);
  }
});
