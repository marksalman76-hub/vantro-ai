const fs = require('fs');
const path = require('path');

const rootRoutePath = path.join(__dirname, '..', 'app', 'api', 'agents', 'route.ts');
const catchAllRoutePath = path.join(__dirname, '..', 'app', 'api', 'agents', '[...path]', 'route.ts');
const rootRouteExists = fs.existsSync(rootRoutePath);
const catchAllRouteExists = fs.existsSync(catchAllRoutePath);
const source = catchAllRouteExists ? fs.readFileSync(catchAllRoutePath, 'utf8') : '';

const checks = [
  {
    name: 'provides GET /api/agents for agent discovery',
    pass: rootRouteExists,
  },
  {
    name: 'provides /api/agents/[...path] for agent run requests',
    pass: catchAllRouteExists,
  },
  {
    name: 'detects incoming content type',
    pass: catchAllRouteExists && (/contentType\s*=/.test(source) || /content-type/i.test(source)),
  },
  {
    name: 'forwards multipart bodies as binary data',
    pass: catchAllRouteExists && /arrayBuffer\(\)/.test(source) && /Buffer\.from/.test(source),
  },
  {
    name: 'does not force JSON content type for every proxied request',
    pass: catchAllRouteExists && !/headers:\s*\{\s*Authorization:\s*token,\s*["']Content-Type["']:\s*["']application\/json["']\s*\}/.test(source),
  },
];

const failed = checks.filter((check) => !check.pass);

if (failed.length) {
  console.error('Agent proxy upload regression check failed:');
  for (const check of failed) console.error(`- ${check.name}`);
  process.exit(1);
}

console.log('Agent proxy upload regression check passed.');
