from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

HOMEPAGE = '''
<!DOCTYPE html>
<html>
<head>
  <title>VaultCorp</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #0a0e17; color: #e2e8f0; font-family: 'Courier New', monospace; padding: 2rem; }
    .container { max-width: 800px; margin: 0 auto; }
    h1 { color: #00ff88; font-size: 2.5rem; margin-bottom: 0.5rem; }
    .subtitle { color: #64748b; margin-bottom: 2rem; }
    .card { background: #111827; border: 1px solid #1e293b; border-radius: 8px; padding: 1.5rem; margin: 1rem 0; }
    .balance { font-size: 3rem; color: #22d3ee; font-weight: bold; }
    .currency { color: #64748b; font-size: 1.5rem; }
    .status { color: #10b981; }
    input { background: #1e293b; border: 1px solid #374151; color: #e2e8f0; padding: 0.75rem 1rem; border-radius: 6px; width: 300px; font-family: inherit; }
    button { background: #00ff88; color: #0a0e17; border: none; padding: 0.75rem 1.5rem; border-radius: 6px; cursor: pointer; font-weight: bold; font-family: inherit; }
    button:hover { background: #00cc6a; }
    .links { margin-top: 2rem; }
    .links a { color: #64748b; margin-right: 1.5rem; text-decoration: none; }
    .links a:hover { color: #22d3ee; }
    .env-badge { display: inline-block; background: #1e293b; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.8rem; color: #f59e0b; margin-left: 1rem; }
  </style>
</head>
<body>
  <div class="container">
    <h1>VaultCorp <span class="env-badge">{{ env }}</span></h1>
    <p class="subtitle">Decentralized Wallet Management Platform</p>

    <div class="card">
      <p style="color: #64748b; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em;">Total Balance</p>
      <p class="balance">1,337.42 <span class="currency">ETH</span></p>
      <p style="margin-top: 0.5rem; color: #64748b;">&#8776; $4,012,260.00 USD</p>
    </div>

    <div class="card">
      <p style="color: #64748b; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em;">Wallet Lookup</p>
      <form action="/lookup" method="get" style="margin-top: 0.75rem;">
        <input name="wallet" placeholder="Enter wallet address (0x...)" />
        <button type="submit">Lookup</button>
      </form>
    </div>

    <div class="card">
      <p><span class="status">&#9679;</span> System Online</p>
      <p style="color: #64748b; font-size: 0.85rem; margin-top: 0.5rem;">Node: {{ node }} | Version: 0.1.0-INSECURE</p>
    </div>

    <div class="links">
      <a href="/status">/status</a>
      <a href="/health">/health</a>
      <a href="/debug">/debug</a>
    </div>
  </div>
</body>
</html>
'''

LOOKUP_PAGE = '''
<!DOCTYPE html>
<html>
<head>
  <title>VaultCorp - Lookup</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #0a0e17; color: #e2e8f0; font-family: 'Courier New', monospace; padding: 2rem; }
    .container { max-width: 800px; margin: 0 auto; }
    h2 { color: #22d3ee; margin-bottom: 1rem; }
    pre { background: #111827; border: 1px solid #1e293b; border-radius: 8px; padding: 1.5rem; overflow-x: auto; }
    a { color: #00ff88; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="container">
    <h2>Lookup: {{ wallet }}</h2>
    <pre>{{ result }}</pre>
    <p style="margin-top: 1rem;"><a href="/">&#8592; Back to Dashboard</a></p>
  </div>
</body>
</html>
'''


@app.route('/')
def home():
    return render_template_string(
        HOMEPAGE,
        env=os.environ.get('ENVIRONMENT', 'production'),
        node=os.environ.get('HOSTNAME', 'unknown'),
    )


@app.route('/lookup')
def lookup():
    wallet = request.args.get('wallet', '')
    # VULN: command injection via user input passed to shell
    result = subprocess.getoutput(f'echo "Looking up wallet: {wallet}"')
    # VULN: XSS — wallet is rendered unescaped via render_template_string
    return render_template_string(LOOKUP_PAGE, wallet=wallet, result=result)


@app.route('/health')
def health():
    return 'ok', 200


@app.route('/status')
def status():
    return render_template_string('''
    <pre style="background:#0a0e17;color:#e2e8f0;padding:2rem;font-family:monospace;">
VaultCorp Status
================
Version:     0.1.0-INSECURE
Uptime:      unknown
Node:        {{ node }}
Environment: {{ env }}
Python:      {{ python }}
    </pre>
    ''',
        node=os.environ.get('HOSTNAME', 'unknown'),
        env=os.environ.get('ENVIRONMENT', 'production'),
        python=os.environ.get('PYTHON_VERSION', 'unknown'),
    )


@app.route('/debug')
def debug():
    # VULN: debug endpoint exposes ALL environment variables including secrets
    envs = '\n'.join(f'{k}={v}' for k, v in sorted(os.environ.items()))
    return f'''
    <pre style="background:#0a0e17;color:#f59e0b;padding:2rem;font-family:monospace;">
DEBUG — Environment Variables
=============================
{envs}
    </pre>
    '''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
