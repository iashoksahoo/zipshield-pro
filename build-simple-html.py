#!/usr/bin/env python3
"""Build the v3.9 SIMPLE ZipShield HTML.

Keeps the v3.6 <head> + CSS byte-for-byte (same UI look), replaces the body
with one simple panel: pick ZIP -> enter password -> ENCRYPT -> complete.
Everything else (telemetry console, terminal log, metrics, pills, ABORT,
COPY, strength meter, file diagnostics, GEN KEY) is removed.
Native callbacks kept: onZipShieldFile / onZipShieldProgress /
onZipShieldChunk (no-op) / onZipShieldDone / onZipShieldError /
onZipShieldCancelled (no-op). Engine (Java) is unchanged from v3.6.
"""
import pathlib

SRC = pathlib.Path.home() / "workspace/zipshield-v36-apk/assets/zipshield.html"
DST = pathlib.Path.home() / "workspace/zipshield-v37-apk/assets/zipshield.html"

v36 = SRC.read_text()
head = v36[:v36.index("<body>")]

# Header from v3.6, minus the status-cluster badges, version bumped to v3.7.
header = v36[v36.index('<header class="topbar">'):v36.index("</header>") + len("</header>")]
header = header[:header.index('      <div class="status-cluster">')] + "    </header>"
header = header.replace("v3.6 ENCRYPT ONLY", "v3.9 ENCRYPT ONLY")

BODY = (
    "<body>\n"
    '  <div class="workstation">\n'
    + header
    + """
    <!-- NON-BLOCKING ALERT BANNER -->
    <div class="alert-banner" id="alertBanner">
      <span id="alertText"></span>
      <button class="alert-close" id="alertCloseBtn" title="Dismiss">[X]</button>
    </div>

    <!-- SIMPLE PANEL: ZIP + PASSWORD + ENCRYPT + COMPLETE -->
    <main class="grid-main">
      <section class="panel">
        <div class="dropzone" id="dropzone" tabindex="0" role="button" aria-label="Select ZIP for encryption">
          <div class="drop-icon">
            <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
          </div>
          <div class="drop-title" id="dropTitle">Select ZIP to Encrypt</div>
          <div class="drop-sub" id="dropSub">Pick a ZIP, enter your password, tap ENCRYPT.</div>
          <div class="browse-pill" id="browsePill">BROWSE ZIP TO ENCRYPT</div>
        </div>

        <!-- PASSWORD -->
        <div class="input-group">
          <div class="input-label-row"><span>PASSWORD</span></div>
          <div class="password-wrap">
            <div class="pw-field-container">
              <input
                type="password"
                id="passwordInput"
                class="pw-input"
                placeholder="Enter password..."
                autocomplete="new-password"
              />
              <button type="button" class="pw-toggle" id="togglePwBtn" title="Show / Hide Password">
                <svg id="eyeIcon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- ONE BUTTON -->
        <div class="action-row">
          <button type="button" class="btn-primary" id="startBtn" disabled>
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
            <span id="startBtnText">ENCRYPT</span>
          </button>
        </div>

        <!-- PROGRESS (only while running / done) -->
        <div id="progressWrap" style="display:none">
          <div class="progress-header">
            <span class="progress-status" id="progressStatus">Encrypting...</span>
            <span class="progress-pct" id="progressPct">0.0%</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" id="progressFill"></div>
          </div>
        </div>

        <!-- COMPLETE -->
        <div class="header-status-box" id="doneBox" style="display:none">
          <span id="doneText"></span>
        </div>
      </section>
    </main>

    <div style="text-align:center;font-family:var(--font-mono);font-size:11px;color:var(--text-muted);padding:2px 0 8px;">Created by Ashok</div>
  </div>

  <script>
    'use strict';
    const el = {
      alertBanner: document.getElementById('alertBanner'),
      alertText: document.getElementById('alertText'),
      alertCloseBtn: document.getElementById('alertCloseBtn'),
      dropzone: document.getElementById('dropzone'),
      dropTitle: document.getElementById('dropTitle'),
      dropSub: document.getElementById('dropSub'),
      passwordInput: document.getElementById('passwordInput'),
      togglePwBtn: document.getElementById('togglePwBtn'),
      startBtn: document.getElementById('startBtn'),
      startBtnText: document.getElementById('startBtnText'),
      progressWrap: document.getElementById('progressWrap'),
      progressStatus: document.getElementById('progressStatus'),
      progressPct: document.getElementById('progressPct'),
      progressFill: document.getElementById('progressFill'),
      doneBox: document.getElementById('doneBox'),
      doneText: document.getElementById('doneText'),
    };
    const state = { pickedName: '', pickedSize: 0, isRunning: false };

    function showBanner(msg, kind) {
      el.alertText.textContent = msg;
      el.alertBanner.className = 'alert-banner show ' + (kind || 'info');
      el.alertBanner.style.display = 'flex';
    }
    function hideBanner() { el.alertBanner.style.display = 'none'; }

    function formatSize(bytes) {
      if (!bytes) return '0 MB';
      const mb = bytes / 1048576;
      return mb >= 1024 ? (mb / 1024).toFixed(2) + ' GB' : mb.toFixed(2) + ' MB';
    }
    function outputName(name) {
      return name.replace(/\\.zip$/i, '') + '-encrypted.zip';
    }
    function updateStartButton() {
      el.startBtn.disabled = state.isRunning
        || !state.pickedName
        || el.passwordInput.value.length < 4;
    }
    function setRunning(running) {
      state.isRunning = running;
      el.startBtnText.textContent = running ? 'ENCRYPTING...' : 'ENCRYPT';
      updateStartButton();
      if (running) {
        el.progressWrap.style.display = 'block';
        el.progressFill.style.width = '0%';
        el.progressPct.textContent = '0.0%';
        el.progressStatus.textContent = 'Encrypting...';
        el.doneBox.style.display = 'none';
      }
    }

    function pickFile() {
      if (state.isRunning) return;
      if (window.AndroidBridge && window.AndroidBridge.pickFile) window.AndroidBridge.pickFile();
      else showBanner('Open this app on the phone to pick a ZIP.', 'error');
    }
    el.dropzone.addEventListener('click', pickFile);

    el.togglePwBtn.addEventListener('click', () => {
      el.passwordInput.type = el.passwordInput.type === 'password' ? 'text' : 'password';
    });
    el.passwordInput.addEventListener('input', updateStartButton);
    el.alertCloseBtn.addEventListener('click', hideBanner);

    el.startBtn.addEventListener('click', () => {
      if (state.isRunning) return;
      const password = el.passwordInput.value;
      if (!state.pickedName) { showBanner('Pick a ZIP file first.', 'error'); return; }
      if (password.length < 4) { showBanner('Password must be at least 4 characters.', 'error'); return; }
      hideBanner();
      setRunning(true);
      try {
        const res = window.AndroidBridge.startEncrypt(password);
        if (res && res.indexOf('ERR:') === 0) {
          showBanner(res, 'error');
          setRunning(false);
        }
      } catch (e) {
        showBanner('Android encrypt engine not available. Open this app on the phone.', 'error');
        setRunning(false);
      }
    });

    // Native callbacks (called by Android via evaluateJavascript)
    window.onZipShieldFile = function(name, size) {
      state.pickedName = name;
      state.pickedSize = size;
      el.dropTitle.textContent = name;
      el.dropSub.textContent = formatSize(size) + '  ->  ' + outputName(name);
      el.doneBox.style.display = 'none';
      updateStartButton();
    };
    window.onZipShieldProgress = function(pct, processed, total, speedMBs, etaSec, status) {
      el.progressPct.textContent = pct.toFixed(1) + '%';
      el.progressFill.style.width = Math.min(100, pct) + '%';
      if (status) el.progressStatus.textContent = status;
    };
    window.onZipShieldChunk = function(idx, totalChunks) { /* no-op: simple UI has no chunk counter */ };
    window.onZipShieldDone = function(outName, shaShort, elapsedSec, fileCount) {
      el.progressPct.textContent = '100.0%';
      el.progressFill.style.width = '100%';
      el.progressStatus.textContent = 'Complete';
      el.doneText.textContent = 'Complete - "' + outName + '" saved in Downloads > ZipShield (' + elapsedSec + 's). Open it in File Manager with your password.';
      el.doneBox.style.display = 'block';
      showBanner('COMPLETE: "' + outName + '" created in Downloads > ZipShield.', 'success');
      setRunning(false);
    };
    window.onZipShieldError = function(message) {
      el.progressStatus.textContent = 'ERROR // ' + message;
      showBanner('ERROR: ' + message, 'error');
      setRunning(false);
    };
    window.onZipShieldCancelled = function() {
      el.progressStatus.textContent = 'Cancelled';
      setRunning(false);
    };

    updateStartButton();
  </script>
</body>
</html>
"""
)

DST.write_text(head + BODY)
print("wrote", DST, len(head + BODY), "bytes")
print("head kept from v3.6:", len(head), "bytes")
