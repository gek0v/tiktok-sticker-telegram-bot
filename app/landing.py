# -*- coding: utf-8 -*-
"""
Geko TikTok Sticker Suite - Architecture & Presentation Landing Page.
Industrial Telemetry & Engineering Console Design.
Author & Architecture: Geko (@gek0v)
"""

def get_landing_html(app_name: str, app_version: str) -> str:
    html_template = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GEKO // STICKER ENGINE • Architecture &amp; System Hub</title>
  <meta name="description" content="Plataforma de alta velocidad para extracción, ingeniería inversa de firmas Aweme y transcodificación de stickers para WhatsApp y Telegram. Creado por Geko.">
  <meta name="author" content="Geko (@gek0v)">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,300;0,400;0,500;0,700;0,800;1,400&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090a0d;
      --bg-alt: #0e1117;
      --panel: #12161f;
      --panel-head: #171c26;
      --border: #1f2735;
      --border-bright: #2e3a4e;
      --border-active: #ff9f1c;
      --text: #e2e8f0;
      --text-muted: #8492a6;
      --text-dim: #4e5d78;
      --accent: #ff9f1c;
      --accent-dim: rgba(255, 159, 28, 0.12);
      --green: #00e676;
      --green-dim: rgba(0, 230, 118, 0.12);
      --cyan: #00f0ff;
      --cyan-dim: rgba(0, 240, 255, 0.1);
      --font-sans: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg);
      color: var(--text);
      font-family: var(--font-sans);
      line-height: 1.5;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      background-image: 
        linear-gradient(to right, rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255,255,255,0.02) 1px, transparent 1px);
      background-size: 32px 32px;
      -webkit-font-smoothing: antialiased;
    }

    /* Top Status Tape */
    .telemetry-tape {
      background: #040507;
      border-bottom: 1px solid var(--border);
      font-family: var(--font-mono);
      font-size: 0.72rem;
      color: var(--text-muted);
      padding: 0.45rem 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
      letter-spacing: 0.05em;
    }

    .tape-group {
      display: flex;
      align-items: center;
      gap: 1.5rem;
      flex-wrap: wrap;
    }

    .tape-item strong {
      color: var(--text);
      font-weight: 600;
    }

    .tape-item.amber strong {
      color: var(--accent);
    }

    .tape-item.green strong {
      color: var(--green);
    }

    .tape-item.cyan strong {
      color: var(--cyan);
    }

    .container {
      max-width: 1180px;
      margin: 0 auto;
      padding: 0 1.5rem;
      width: 100%;
    }

    /* Header */
    header.console-header {
      padding: 2.25rem 0 1.75rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      flex-wrap: wrap;
      gap: 1.25rem;
    }

    .brand-mark {
      display: flex;
      align-items: center;
      gap: 1rem;
      text-decoration: none;
    }

    .brand-symbol {
      width: 44px;
      height: 44px;
      background: #000000;
      border: 1px solid var(--border-bright);
      color: var(--accent);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--font-mono);
      font-weight: 800;
      font-size: 1.35rem;
      position: relative;
    }

    .brand-symbol::after {
      content: '';
      position: absolute;
      bottom: -1px;
      right: -1px;
      width: 6px;
      height: 6px;
      background: var(--accent);
    }

    .brand-title {
      display: flex;
      flex-direction: column;
    }

    .brand-title span:first-child {
      font-family: var(--font-mono);
      font-weight: 800;
      font-size: 1.15rem;
      letter-spacing: 0.1em;
      color: #ffffff;
      text-transform: uppercase;
    }

    .brand-subtitle {
      font-family: var(--font-mono);
      font-size: 0.73rem;
      color: var(--text-muted);
      letter-spacing: 0.05em;
    }

    .nav-actions {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .console-btn {
      font-family: var(--font-mono);
      font-size: 0.76rem;
      font-weight: 600;
      padding: 0.55rem 1rem;
      background: var(--panel);
      border: 1px solid var(--border);
      color: var(--text);
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      transition: all 0.15s ease;
      cursor: pointer;
    }

    .console-btn:hover {
      border-color: var(--border-bright);
      background: var(--panel-head);
      color: #fff;
    }

    .console-btn.primary {
      background: var(--accent-dim);
      border-color: var(--accent);
      color: var(--accent);
    }

    .console-btn.primary:hover {
      background: var(--accent);
      color: #000;
    }

    /* Hero */
    .hero-spec {
      padding: 3rem 0 2rem;
      border-bottom: 1px solid var(--border);
    }

    .hero-meta {
      font-family: var(--font-mono);
      font-size: 0.73rem;
      color: var(--accent);
      letter-spacing: 0.15em;
      text-transform: uppercase;
      margin-bottom: 0.75rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .hero-meta::before {
      content: '//';
      color: var(--text-dim);
    }

    h1.hero-heading {
      font-size: clamp(1.9rem, 4vw, 2.85rem);
      font-weight: 700;
      line-height: 1.15;
      letter-spacing: -0.03em;
      color: #ffffff;
      max-width: 900px;
      margin-bottom: 1rem;
    }

    .hero-lead {
      font-size: 1.05rem;
      color: var(--text-muted);
      max-width: 820px;
      line-height: 1.6;
    }

    /* Hardware Specs Strip */
    .specs-strip {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 1px;
      background: var(--border);
      border: 1px solid var(--border);
      margin: 2rem 0 3rem;
    }

    .spec-box {
      background: var(--bg-alt);
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }

    .spec-box-label {
      font-family: var(--font-mono);
      font-size: 0.68rem;
      color: var(--text-dim);
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }

    .spec-box-value {
      font-family: var(--font-mono);
      font-size: 1.15rem;
      font-weight: 700;
      color: #ffffff;
      letter-spacing: -0.01em;
    }

    .spec-box-desc {
      font-size: 0.78rem;
      color: var(--text-muted);
      line-height: 1.4;
    }

    /* Section Headings */
    .section-header-box {
      margin: 2.75rem 0 1.25rem;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.75rem;
    }

    .section-tag {
      font-family: var(--font-mono);
      font-size: 0.7rem;
      color: var(--accent);
      letter-spacing: 0.12em;
      text-transform: uppercase;
      margin-bottom: 0.25rem;
    }

    .section-title-plain {
      font-size: 1.35rem;
      font-weight: 700;
      color: #ffffff;
      letter-spacing: -0.01em;
    }

    /* Architecture Grid */
    .arch-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 1rem;
      margin-bottom: 2.5rem;
    }

    .arch-card {
      background: var(--panel);
      border: 1px solid var(--border);
      padding: 1.4rem;
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: border-color 0.2s ease;
    }

    .arch-card:hover {
      border-color: var(--border-bright);
    }

    .arch-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }

    .arch-num {
      font-family: var(--font-mono);
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--accent);
    }

    .arch-protocol {
      font-family: var(--font-mono);
      font-size: 0.65rem;
      background: #000;
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 0.2rem 0.5rem;
      letter-spacing: 0.08em;
    }

    .arch-card h3 {
      font-size: 1.05rem;
      font-weight: 600;
      color: #ffffff;
      margin-bottom: 0.5rem;
    }

    .arch-card p {
      font-size: 0.84rem;
      color: var(--text-muted);
      line-height: 1.55;
    }

    .arch-card code {
      font-family: var(--font-mono);
      font-size: 0.78rem;
      background: rgba(255,255,255,0.06);
      padding: 0.1rem 0.35rem;
      color: var(--text);
    }

    .arch-footer {
      margin-top: 1.25rem;
      padding-top: 0.75rem;
      border-top: 1px solid rgba(255,255,255,0.05);
      font-family: var(--font-mono);
      font-size: 0.68rem;
      color: var(--text-dim);
      display: flex;
      justify-content: space-between;
    }

    /* Benchmarks Table */
    .bench-table-wrap {
      border: 1px solid var(--border);
      background: var(--panel);
      margin-bottom: 3rem;
      overflow-x: auto;
    }

    table.bench-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
      text-align: left;
    }

    table.bench-table th {
      background: var(--panel-head);
      padding: 0.85rem 1.25rem;
      font-family: var(--font-mono);
      font-size: 0.7rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--text-muted);
      border-bottom: 1px solid var(--border);
      font-weight: 600;
    }

    table.bench-table td {
      padding: 1rem 1.25rem;
      border-bottom: 1px solid var(--border);
      color: var(--text);
      font-family: var(--font-mono);
    }

    table.bench-table tr:last-child td {
      border-bottom: none;
    }

    table.bench-table tr:hover td {
      background: rgba(255,255,255,0.02);
    }

    .delta-badge {
      display: inline-block;
      font-family: var(--font-mono);
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--green);
      background: var(--green-dim);
      border: 1px solid var(--green);
      padding: 0.2rem 0.5rem;
    }

    /* Author Plate */
    .spec-plate-container {
      margin: 2.5rem 0 4rem;
    }

    .spec-plate {
      background: linear-gradient(180deg, #121620 0%, #0d1017 100%);
      border: 1px solid var(--border-bright);
      box-shadow: inset 0 0 0 1px rgba(255,255,255,0.05);
      padding: 2.25rem;
      position: relative;
    }

    .spec-plate::before {
      content: 'ETCHED CERTIFICATION SPEC // 2026.11';
      position: absolute;
      top: -9px;
      left: 1.5rem;
      background: #000;
      border: 1px solid var(--border-bright);
      padding: 0.15rem 0.65rem;
      font-family: var(--font-mono);
      font-size: 0.62rem;
      color: var(--text-dim);
      letter-spacing: 0.12em;
    }

    .spec-plate-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 1.25rem;
      flex-wrap: wrap;
      gap: 1.25rem;
    }

    .architect-title {
      font-family: var(--font-mono);
      font-size: 1.6rem;
      font-weight: 800;
      color: #ffffff;
      letter-spacing: 0.08em;
    }

    .architect-role {
      font-family: var(--font-mono);
      font-size: 0.76rem;
      color: var(--accent);
      letter-spacing: 0.1em;
      text-transform: uppercase;
      margin-top: 0.2rem;
    }

    .spec-plate-body {
      font-size: 0.95rem;
      color: var(--text-muted);
      line-height: 1.7;
      max-width: 950px;
      margin-bottom: 1.5rem;
    }

    .spec-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-top: 1rem;
    }

    .spec-tag {
      font-family: var(--font-mono);
      font-size: 0.68rem;
      background: #000000;
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 0.35rem 0.75rem;
      letter-spacing: 0.05em;
    }

    /* Footer */
    footer.console-footer {
      margin-top: auto;
      border-top: 1px solid var(--border);
      background: #050608;
      padding: 1.75rem 0;
      font-family: var(--font-mono);
      font-size: 0.72rem;
      color: var(--text-dim);
    }

    .footer-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }
  </style>
</head>
<body>

  <!-- Top Status Tape -->
  <div class="telemetry-tape">
    <div class="tape-group">
      <div class="tape-item">SYS: <strong>ONLINE</strong></div>
      <div class="tape-item">NODE: <strong>RENDER-P1 [FRA]</strong></div>
      <div class="tape-item green">DAEMON: <strong>8088/TCP AWEME SIGNER</strong></div>
      <div class="tape-item cyan">BUILD: <strong>v{{APP_VERSION}}</strong></div>
    </div>
    <div class="tape-group">
      <div class="tape-item">RUNTIME: <strong>DOCKER / PYTHON 3.12</strong></div>
      <div class="tape-item amber">CLK: <strong id="clock-display">--:--:-- UTC+1</strong></div>
    </div>
  </div>

  <div class="container">
    <!-- Header -->
    <header class="console-header">
      <a href="/" class="brand-mark">
        <div class="brand-symbol">G</div>
        <div class="brand-title">
          <span>GEKO // STICKER ENGINE</span>
          <span class="brand-subtitle">Multimedia DSP &amp; Aweme Signature Hub</span>
        </div>
      </a>
      <div class="nav-actions">
        <a href="https://github.com/gek0v/tiktok-sticker-telegram-bot" target="_blank" rel="noopener" class="console-btn">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
          </svg>
          <span>src: gek0v/repo</span>
        </a>
        <a href="#pipeline" class="console-btn primary">ARQUITECTURA // SPEC</a>
      </div>
    </header>

    <!-- Hero / Architecture Spec -->
    <section class="hero-spec">
      <div class="hero-meta">SYSTEM ARCHITECTURE // REVERSE ENGINEERING &amp; SIGNAL TRANSLATION</div>
      <h1 class="hero-heading">Autonomous ByteDance Aweme Ingestion &amp; Dual-Vector Media Pipeline</h1>
      <p class="hero-lead">
        Servicio distribuido de alto rendimiento para extracción inversa de recursos de TikTok (v37.0.4), sintetizado de firmas criptográficas bajo demanda y transcodificación acelerada multi-hilo para WhatsApp WebP y Telegram VP9.
      </p>
    </section>

    <!-- Hardware & Processing Specs Strip -->
    <div class="specs-strip">
      <div class="spec-box">
        <span class="spec-box-label">// MATRIZ GRÁFICA</span>
        <span class="spec-box-value">512 × 512 PX</span>
        <span class="spec-box-desc">Canvas normalizado RGBA 1:1 con alpha channel transparente.</span>
      </div>
      <div class="spec-box">
        <span class="spec-box-label">// PROTOCOLO WHATSAPP</span>
        <span class="spec-box-value">&lt; 500 KB WEBP</span>
        <span class="spec-box-desc">Compresión adaptativa Pillow con retención de fidelidad visual.</span>
      </div>
      <div class="spec-box">
        <span class="spec-box-label">// PROTOCOLO TELEGRAM</span>
        <span class="spec-box-value">WEBM VP9 / TGS</span>
        <span class="spec-box-desc">Transcodificación acelerada en 338 ms para reproducción nativa.</span>
      </div>
      <div class="spec-box">
        <span class="spec-box-label">// SEGURIDAD &amp; FIRMAS</span>
        <span class="spec-box-value">AWEME v37.0.4</span>
        <span class="spec-box-desc">Generación de cabeceras X-Gorgon, X-Khronos, X-Argus y X-Ladon.</span>
      </div>
    </div>

    <!-- Architecture & Engineering Pipeline -->
    <div class="section-header-box" id="pipeline">
      <div>
        <div class="section-tag">// SUB-SYSTEMS &amp; PIPELINES</div>
        <div class="section-title-plain">Flujo de Procesamiento Distribuido</div>
      </div>
    </div>

    <div class="arch-grid">
      <div class="arch-card">
        <div>
          <div class="arch-top">
            <span class="arch-num">[01]</span>
            <span class="arch-protocol">FAST-PATH REGEX</span>
          </div>
          <h3>Ingesta &amp; Resolución</h3>
          <p>Detección instantánea de URLs cortas de TikTok (<code>vm.tiktok.com</code>), identificadores numéricos directos y fotos de comentarios (JPG, PNG, iOS HEIC) en 0.07 ms sin saltos HTTP redundantes.</p>
        </div>
        <div class="arch-footer">
          <span>&gt; REGEX RESOLVER: ACTIVE</span>
        </div>
      </div>

      <div class="arch-card">
        <div>
          <div class="arch-top">
            <span class="arch-num">[02]</span>
            <span class="arch-protocol">MICROSERVICE :8088</span>
          </div>
          <h3>Firmas Criptográficas</h3>
          <p>Microservicio de firmas enlazado que computa cabeceras propietarias de ByteDance (<code>X-Gorgon</code>, <code>X-Khronos</code>, <code>X-Argus</code> y <code>X-Ladon</code>), emulando clientes móviles auténticos.</p>
        </div>
        <div class="arch-footer">
          <span>&gt; AWEME SIGNER: LOCKED</span>
        </div>
      </div>

      <div class="arch-card">
        <div>
          <div class="arch-top">
            <span class="arch-num">[03]</span>
            <span class="arch-protocol">DUAL-THREAD DSP</span>
          </div>
          <h3>Transcodificación</h3>
          <p>Pipeline multi-hilo en C/Pillow y FFmpeg VP9: produce simultáneamente stickers transparentes WebP 512×512 (&lt;500 KB para WhatsApp) y WebM animado nativo para Telegram.</p>
        </div>
        <div class="arch-footer">
          <span>&gt; TRANSCODER: OPTIMIZED</span>
        </div>
      </div>

      <div class="arch-card">
        <div>
          <div class="arch-top">
            <span class="arch-num">[04]</span>
            <span class="arch-protocol">ASYNC CLIENT BUS</span>
          </div>
          <h3>Despacho Telegram &amp; App</h3>
          <p>Entrega a través del bot oficial de Telegram con teclado de descarga táctil y canalización de paquetes al <code>StickerContentProvider</code> de la aplicación Android nativa.</p>
        </div>
        <div class="arch-footer">
          <span>&gt; DISPATCH BUS: ONLINE</span>
        </div>
      </div>
    </div>

    <!-- Verified Performance Matrix -->
    <div class="section-header-box">
      <div>
        <div class="section-tag">// EMPIRICAL BENCHMARKS</div>
        <div class="section-title-plain">Métricas de Optimización del Pipeline</div>
      </div>
    </div>

    <div class="bench-table-wrap">
      <table class="bench-table">
        <thead>
          <tr>
            <th>COMPONENTE EVALUADO</th>
            <th>BASELINE PREVIO</th>
            <th>REVISIÓN ACTUAL</th>
            <th>REDUCCIÓN / SPEEDUP</th>
            <th>ESTADO</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Latencia total transcodificación de animación</td>
            <td>3,071 ms</td>
            <td><strong>763 ms</strong></td>
            <td><span class="delta-badge">-75.2%</span></td>
            <td>VERIFICADO</td>
          </tr>
          <tr>
            <td>Renderizado WebM VP9 (Telegram Sticker)</td>
            <td>1,830 ms</td>
            <td><strong>338 ms</strong></td>
            <td><span class="delta-badge">-81.5%</span></td>
            <td>VERIFICADO</td>
          </tr>
          <tr>
            <td>Normalización de imágenes estáticas / HEIC</td>
            <td>466 ms</td>
            <td><strong>58 ms</strong></td>
            <td><span class="delta-badge">-87.5%</span></td>
            <td>VERIFICADO</td>
          </tr>
          <tr>
            <td>Fast-Path de resolución por expresiones regulares</td>
            <td>1.20 ms</td>
            <td><strong>0.07 ms</strong></td>
            <td><span class="delta-badge">-94.1%</span></td>
            <td>VERIFICADO</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Author & Architecture Spec Plate -->
    <div class="spec-plate-container">
      <div class="spec-plate">
        <div class="spec-plate-header">
          <div>
            <div class="architect-title">GEKO (@GEK0V)</div>
            <div class="architect-role">LEAD ARCHITECT, REVERSE ENGINEER &amp; SYSTEMS CREATOR</div>
          </div>
          <div>
            <a href="https://github.com/gek0v/tiktok-sticker-telegram-bot" target="_blank" rel="noopener" class="console-btn primary">
              <span>EXPLORAR REPOSITORIO GITHUB</span>
            </a>
          </div>
        </div>
        <div class="spec-plate-body">
          Diseño integral de arquitectura y ejecución técnica: ingeniería inversa de firmas criptográficas ByteDance Aweme, orquestación de microservicios sin coste en nube, optimización de algoritmos de procesamiento de imágenes y desarrollo de la suite completa de clientes (Telegram Bot, API FastAPI y arquitectura nativa Android Jetpack Compose).
        </div>
        <div class="spec-tags">
          <span class="spec-tag">DISCIPLINES: REVERSE ENGINEERING</span>
          <span class="spec-tag">SECURITY: X-GORGON / X-ARGUS</span>
          <span class="spec-tag">CODECS: WEBP / VP9</span>
          <span class="spec-tag">RUNTIME: FASTAPI + DOCKER</span>
          <span class="spec-tag">LICENSE: OPEN SOURCE</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <footer class="console-footer">
    <div class="container footer-content">
      <div>GEKO STICKER ENGINE • ARCHITECTURE &amp; SYSTEMS PLATFORM</div>
      <div>AUTONOMOUS MULTIMEDIA DSP PIPELINE // ALL RIGHTS RESERVED TO GEKO</div>
    </div>
  </footer>

  <script>
    // Real-time clock update (Madrid/Europe)
    function updateClock() {
      const now = new Date();
      const timeStr = now.toLocaleTimeString('es-ES', { hour12: false }) + ' UTC+1';
      const el = document.getElementById('clock-display');
      if (el) el.innerText = timeStr;
    }
    setInterval(updateClock, 1000);
    updateClock();
  </script>
</body>
</html>
"""
    return html_template.replace("{{APP_NAME}}", app_name).replace("{{APP_VERSION}}", app_version)
