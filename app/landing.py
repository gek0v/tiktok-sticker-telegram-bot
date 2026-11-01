# -*- coding: utf-8 -*-
"""
Landing page & Uptime monitor view for Geko TikTok Sticker Suite.
Designed for 24/7 keep-alive monitoring via UptimeRobot and public presentation.
Author & Architecture: Geko (@gek0v)
"""

def get_landing_html(app_name: str, app_version: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Geko Sticker Suite • TikTok to WhatsApp &amp; Telegram</title>
  <meta name="description" content="Plataforma de alta velocidad para extracción, ingeniería inversa de firmas Aweme y transcodificación de stickers para WhatsApp y Telegram. Desarrollado por Geko.">
  <meta name="author" content="Geko (@gek0v)">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #090d16;
      --card-bg: rgba(18, 24, 38, 0.75);
      --card-border: rgba(255, 255, 255, 0.08);
      --primary: #fe2c55;
      --accent: #25f4ee;
      --wa-green: #25d366;
      --tg-blue: #24a1de;
      --status-ok: #10b981;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --code-bg: rgba(15, 23, 42, 0.85);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg);
      background-image: 
        radial-gradient(circle at 15% 15%, rgba(254, 44, 85, 0.12) 0%, transparent 40%),
        radial-gradient(circle at 85% 20%, rgba(37, 244, 238, 0.10) 0%, transparent 45%),
        radial-gradient(circle at 50% 80%, rgba(37, 211, 102, 0.08) 0%, transparent 50%);
      color: var(--text);
      min-height: 100vh;
      line-height: 1.6;
      padding: 0 1.25rem 4rem;
    }}

    .container {{
      max-width: 1040px;
      margin: 0 auto;
    }}

    /* Top Nav */
    header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1.75rem 0;
      border-bottom: 1px solid var(--card-border);
      margin-bottom: 2.5rem;
    }}

    .logo-container {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      text-decoration: none;
      color: inherit;
    }}

    .logo-badge {{
      background: linear-gradient(135deg, var(--primary), #b51739);
      color: white;
      font-weight: 800;
      font-size: 0.85rem;
      padding: 0.35rem 0.75rem;
      border-radius: 8px;
      letter-spacing: 0.05em;
      box-shadow: 0 4px 15px rgba(254, 44, 85, 0.35);
    }}

    .logo-title {{
      font-weight: 700;
      font-size: 1.15rem;
      letter-spacing: -0.02em;
    }}

    .nav-links {{
      display: flex;
      align-items: center;
      gap: 1rem;
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.55rem 1.15rem;
      border-radius: 9999px;
      font-size: 0.875rem;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.2s ease;
      border: 1px solid transparent;
      cursor: pointer;
    }}

    .btn-github {{
      background: rgba(255, 255, 255, 0.06);
      color: var(--text);
      border-color: var(--card-border);
    }}

    .btn-github:hover {{
      background: rgba(255, 255, 255, 0.12);
      border-color: rgba(255, 255, 255, 0.2);
      transform: translateY(-1px);
    }}

    /* Hero Section */
    .hero {{
      text-align: center;
      padding: 2.5rem 0 3.5rem;
    }}

    .author-pill {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.12);
      padding: 0.4rem 1rem;
      border-radius: 9999px;
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-bottom: 1.5rem;
    }}

    .author-pill strong {{
      color: var(--accent);
      font-weight: 700;
    }}

    .hero h1 {{
      font-size: clamp(2.2rem, 5vw, 3.4rem);
      font-weight: 800;
      letter-spacing: -0.03em;
      line-height: 1.15;
      margin-bottom: 1.25rem;
      background: linear-gradient(135deg, #ffffff 40%, #94a3b8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .hero p {{
      font-size: 1.15rem;
      color: var(--text-muted);
      max-width: 680px;
      margin: 0 auto 2rem;
    }}

    /* Monitor & Status Card (Special for UptimeRobot) */
    .monitor-card {{
      background: linear-gradient(145deg, rgba(16, 185, 129, 0.07), rgba(15, 23, 42, 0.85));
      border: 1px solid rgba(16, 185, 129, 0.3);
      border-radius: 18px;
      padding: 1.75rem;
      margin-bottom: 3.5rem;
      backdrop-filter: blur(12px);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    }}

    .monitor-header {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1.25rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.07);
    }}

    .status-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.6rem;
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid var(--status-ok);
      color: #6ee7b7;
      padding: 0.4rem 0.9rem;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-weight: 700;
      letter-spacing: 0.02em;
    }}

    .status-dot {{
      width: 10px;
      height: 10px;
      background-color: var(--status-ok);
      border-radius: 50%;
      box-shadow: 0 0 12px var(--status-ok);
      animation: pulse 2s infinite;
    }}

    @keyframes pulse {{
      0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
      70% {{ transform: scale(1.1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }}
      100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
    }}

    .monitor-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.25rem;
      margin-top: 1rem;
    }}

    .stat-box {{
      background: rgba(0, 0, 0, 0.25);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 1rem;
    }}

    .stat-label {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-muted);
      margin-bottom: 0.35rem;
    }}

    .stat-value {{
      font-size: 1.2rem;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      color: #ffffff;
    }}

    .uptime-note {{
      margin-top: 1.25rem;
      font-size: 0.85rem;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(255, 255, 255, 0.03);
      padding: 0.75rem 1rem;
      border-radius: 10px;
    }}

    .uptime-note code {{
      font-family: 'JetBrains Mono', monospace;
      color: var(--accent);
      background: rgba(37, 244, 238, 0.1);
      padding: 0.15rem 0.4rem;
      border-radius: 4px;
    }}

    /* Section Titles */
    .section-title {{
      font-size: 1.6rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      margin-bottom: 1.5rem;
      display: flex;
      align-items: center;
      gap: 0.6rem;
    }}

    /* Workflow Cards */
    .grid-workflow {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 1.25rem;
      margin-bottom: 3.5rem;
    }}

    .card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 1.5rem;
      transition: transform 0.2s ease, border-color 0.2s ease;
      position: relative;
      overflow: hidden;
    }}

    .card:hover {{
      transform: translateY(-3px);
      border-color: rgba(255, 255, 255, 0.18);
    }}

    .step-number {{
      position: absolute;
      top: 1rem;
      right: 1.25rem;
      font-size: 2.2rem;
      font-weight: 800;
      font-family: 'JetBrains Mono', monospace;
      color: rgba(255, 255, 255, 0.04);
      user-select: none;
    }}

    .card-icon {{
      width: 42px;
      height: 42px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.25rem;
      margin-bottom: 1rem;
    }}

    .icon-input {{ background: rgba(254, 44, 85, 0.15); color: var(--primary); }}
    .icon-crypto {{ background: rgba(37, 244, 238, 0.15); color: var(--accent); }}
    .icon-transcode {{ background: rgba(37, 211, 102, 0.15); color: var(--wa-green); }}
    .icon-deliver {{ background: rgba(36, 161, 222, 0.15); color: var(--tg-blue); }}

    .card h3 {{
      font-size: 1.1rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
    }}

    .card p {{
      font-size: 0.9rem;
      color: var(--text-muted);
      line-height: 1.5;
    }}

    /* Benchmark highlights */
    .benchmark-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 1.75rem;
      margin-bottom: 3.5rem;
    }}

    .bench-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.25rem;
      margin-top: 1.25rem;
    }}

    .bench-item {{
      border-left: 3px solid var(--accent);
      padding-left: 1rem;
    }}

    .bench-number {{
      font-size: 1.6rem;
      font-weight: 800;
      font-family: 'JetBrains Mono', monospace;
      color: #ffffff;
    }}

    .bench-number span {{
      color: var(--accent);
      font-size: 0.9rem;
    }}

    .bench-desc {{
      font-size: 0.85rem;
      color: var(--text-muted);
    }}

    /* Author & Credits Footer Card */
    .credits-card {{
      background: linear-gradient(135deg, rgba(254, 44, 85, 0.08), rgba(37, 244, 238, 0.08));
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 18px;
      padding: 2.25rem;
      text-align: center;
      position: relative;
    }}

    .credits-avatar {{
      width: 72px;
      height: 72px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--primary), var(--accent));
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.8rem;
      font-weight: 800;
      margin: 0 auto 1.25rem;
      color: #090d16;
      box-shadow: 0 0 25px rgba(37, 244, 238, 0.3);
    }}

    .credits-title {{
      font-size: 1.35rem;
      font-weight: 800;
      margin-bottom: 0.25rem;
    }}

    .credits-subtitle {{
      color: var(--accent);
      font-weight: 600;
      font-size: 0.95rem;
      margin-bottom: 1rem;
    }}

    .credits-bio {{
      max-width: 620px;
      margin: 0 auto 1.5rem;
      color: var(--text-muted);
      font-size: 0.95rem;
    }}

    .credits-links {{
      display: flex;
      justify-content: center;
      gap: 1rem;
      flex-wrap: wrap;
    }}

    footer {{
      margin-top: 3rem;
      text-align: center;
      font-size: 0.8rem;
      color: rgba(255, 255, 255, 0.4);
    }}
  </style>
</head>
<body>

  <div class="container">
    <!-- Header -->
    <header>
      <a href="/" class="logo-container">
        <span class="logo-badge">GEKO SUITE</span>
        <span class="logo-title">Sticker Engine</span>
      </a>
      <div class="nav-links">
        <a href="https://github.com/gek0v/tiktok-sticker-telegram-bot" target="_blank" rel="noopener" class="btn btn-github">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
          </svg>
          GitHub @gek0v
        </a>
      </div>
    </header>

    <!-- Hero -->
    <section class="hero">
      <div class="author-pill">
        <span>Diseñado y construido por</span>
        <strong>Geko (@gek0v)</strong>
      </div>
      <h1>TikTok &amp; Multimedia Sticker Engine</h1>
      <p>Microservicios de alto rendimiento para extracción inversa de TikTok Aweme, firmado criptográfico y transcodificación dual para WhatsApp y Telegram.</p>
    </section>

    <!-- Monitor & Health Section for UptimeRobot -->
    <section class="monitor-card" id="status-section">
      <div class="monitor-header">
        <div>
          <h2 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 0.25rem;">Monitor de Disponibilidad (24/7 Keep-Alive)</h2>
          <p style="font-size: 0.85rem; color: var(--text-muted);">Compatible con sondeos periódicos de UpTimeRobot / Health Monitors</p>
        </div>
        <div class="status-badge" id="live-badge">
          <span class="status-dot"></span>
          <span id="status-text">SISTEMA ACTIVO</span>
        </div>
      </div>

      <div class="monitor-grid">
        <div class="stat-box">
          <div class="stat-label">Estado de Servicio</div>
          <div class="stat-value" id="stat-status" style="color: #6ee7b7;">OPERATIVO</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Latencia Healthcheck</div>
          <div class="stat-value" id="stat-ping">-- ms</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Firma Criptográfica</div>
          <div class="stat-value" id="stat-signer" style="color: var(--accent);">REMOTE 8088</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Versión Build</div>
          <div class="stat-value">{app_version}</div>
        </div>
      </div>

      <div class="uptime-note">
        <span>⚡ <strong>Tip para UpTimeRobot:</strong> Configura un monitor de tipo <strong>HTTP(s)</strong> apuntando a <code>/</code> o a <code>/health</code> con intervalo de <strong>5 a 10 minutos</strong> para mantener el contenedor de Render siempre despierto y evitar tiempos de arranque en frío.</span>
      </div>
    </section>

    <!-- Cómo Funciona -->
    <h2 class="section-title">
      <span>⚙️</span>
      <span>¿Cómo Funciona el Sistema?</span>
    </h2>

    <div class="grid-workflow">
      <div class="card">
        <div class="step-number">01</div>
        <div class="card-icon icon-input">🔗</div>
        <h3>Ingesta Rápida</h3>
        <p>Procesa enlaces directos de TikTok, enlaces compartidos (<code>vm.tiktok.com</code>) o imágenes enviadas por el usuario (JPG, PNG, HEIC de iOS) mediante extracción regex optimizada sin saltos HTTP innecesarios.</p>
      </div>

      <div class="card">
        <div class="step-number">02</div>
        <div class="card-icon icon-crypto">🔐</div>
        <h3>Firmado Criptográfico</h3>
        <p>Un microservicio dedicado genera dinámicamente las firmas propietarias de ByteDance (<code>X-Gorgon</code>, <code>X-Khronos</code>, <code>X-Argus</code> y <code>X-Ladon</code>), simulando peticiones legítimas de la app TikTok v37.0.4.</p>
      </div>

      <div class="card">
        <div class="step-number">03</div>
        <div class="card-icon icon-transcode">⚡</div>
        <h3>Transcodificación Dual</h3>
        <p>Pipeline paralelo multi-hilo: genera stickers <strong>WebP transparentes (512×512)</strong> bajo las estrictas directrices de WhatsApp (&lt;500 KB) y simultáneamente <strong>WebM VP9 animado</strong> para Telegram.</p>
      </div>

      <div class="card">
        <div class="step-number">04</div>
        <div class="card-icon icon-deliver">🤖</div>
        <h3>Distribución Inmediata</h3>
        <p>Entrega instantánea mediante Bot Oficial de Telegram con teclado interactivo de descarga y compatibilidad directa con el <code>StickerContentProvider</code> de la aplicación móvil Android.</p>
      </div>
    </div>

    <!-- Benchmarks -->
    <div class="benchmark-card">
      <h2 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 0.5rem;">🚀 Rendimiento Optimizado (Benchmark Suite)</h2>
      <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1.25rem;">
        Pipeline optimizado con paralelización de salida, flags VP9 en tiempo real (<code>-deadline realtime -cpu-used 6</code>) y resampling bicúbico.
      </p>
      <div class="bench-grid">
        <div class="bench-item">
          <div class="bench-number">-75.2%</div>
          <div class="bench-desc">Reducción en latencia total de animación (3.071 ms &rarr; 763 ms)</div>
        </div>
        <div class="bench-item">
          <div class="bench-number">-81.5%</div>
          <div class="bench-desc">Tiempo de renderizado VP9 Telegram (1.830 ms &rarr; 338 ms)</div>
        </div>
        <div class="bench-item">
          <div class="bench-number">-87.5%</div>
          <div class="bench-desc">Normalización de fotografías estáticas (466 ms &rarr; 58 ms)</div>
        </div>
        <div class="bench-item">
          <div class="bench-number">0.07 <span>ms</span></div>
          <div class="bench-desc">Fast-path de resolución de identificadores TikTok por regex</div>
        </div>
      </div>
    </div>

    <!-- Credits Card -->
    <div class="credits-card">
      <div class="credits-avatar">G</div>
      <h3 class="credits-title">Geko</h3>
      <div class="credits-subtitle">Creador, Desarrollador &amp; Arquitecto de Software</div>
      <p class="credits-bio">
        Diseño integral de la infraestructura, ingeniería inversa de protocolos de ByteDance, optimización de pipelines de transcodificación multimedia a bajo nivel y orquestación del ecosistema distribuido (Telegram Bot + Backend FastAPI + App Android).
      </p>
      <div class="credits-links">
        <a href="https://github.com/gek0v/tiktok-sticker-telegram-bot" target="_blank" rel="noopener" class="btn btn-github">
          <span>Repositorio en GitHub</span>
        </a>
      </div>
    </div>

    <!-- Footer -->
    <footer>
      <p>&copy; 2026 Geko (@gek0v) • Todos los derechos reservados. Desarrollado para alta disponibilidad y monitorización continua.</p>
    </footer>
  </div>

  <script>
    // Live ping monitor for Uptime test
    async function checkHealth() {{
      const start = performance.now();
      try {{
        const res = await fetch('/health');
        const latency = Math.round(performance.now() - start);
        if (res.ok) {{
          const data = await res.json();
          document.getElementById('stat-ping').innerText = latency + ' ms';
          document.getElementById('stat-status').innerText = 'OPERATIVO';
          document.getElementById('stat-status').style.color = '#6ee7b7';
          if (data.signer_mode) {{
            document.getElementById('stat-signer').innerText = data.signer_mode.toUpperCase() + ' :8088';
          }}
        }} else {{
          document.getElementById('stat-status').innerText = 'DEGRADADO (' + res.status + ')';
          document.getElementById('stat-status').style.color = '#f59e0b';
        }}
      }} catch (err) {{
        document.getElementById('stat-status').innerText = 'OFFLINE';
        document.getElementById('stat-status').style.color = '#ef4444';
      }}
    }}
    checkHealth();
    setInterval(checkHealth, 30000);
  </script>
</body>
</html>
"""
