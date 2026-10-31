/* Faint signals behind the work: sleep traces, hardware lines, data streams.
   Thin lines at 4 to 8 % opacity, slow, paused when the tab is hidden, static under reduced motion. */
(function () {
  var c = document.getElementById('signals');
  if (!c || !c.getContext) return;
  var x = c.getContext('2d');
  var still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var W = 0, H = 0, dpr = 1;
  var GREY = '201,187,167', AMB = '242,184,102';

  function size() {
    dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    W = innerWidth; H = innerHeight;
    c.width = Math.round(W * dpr); c.height = Math.round(H * dpr);
    x.setTransform(dpr, 0, 0, dpr, 0, 0);
    build();
  }

  /* seeded random so the circuit board doesn't reshuffle on resize */
  var seed = 7;
  function rnd() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }

  var traces = [], vias = [], streams = [];
  function build() {
    seed = 7; traces = []; vias = []; streams = [];
    var step = 28, n = Math.round((W * H) / 52000) + 6;
    for (var i = 0; i < n; i++) {
      var px = Math.round(rnd() * W / step) * step, py = Math.round(rnd() * H / step) * step, pts = [[px, py]];
      var dir = rnd() < 0.5 ? 0 : 1, len = 3 + Math.floor(rnd() * 5);
      for (var k = 0; k < len; k++) {
        var d = (2 + Math.floor(rnd() * 5)) * step * (rnd() < 0.5 ? -1 : 1);
        if (dir === 0) px += d; else py += d;
        if (rnd() < 0.35) { px += step * (rnd() < 0.5 ? -1 : 1); py += step * (rnd() < 0.5 ? -1 : 1); }
        pts.push([px, py]); dir = 1 - dir;
      }
      traces.push(pts); vias.push(pts[pts.length - 1]);
    }
    var cols = Math.max(3, Math.round(W / 140));
    for (var j = 0; j < cols; j++) {
      var lines = [];
      for (var m = 0; m < 60; m++) lines.push({ ind: Math.floor(rnd() * 4), len: 20 + rnd() * 90, gap: rnd() < 0.18 });
      streams.push({ x: (j + 0.5) * W / cols - 50 + rnd() * 30, speed: 6 + rnd() * 6, lines: lines });
    }
  }

  function line(a, col, w) { x.strokeStyle = 'rgba(' + (col || GREY) + ',' + a + ')'; x.lineWidth = w || 1; }

  /* sleep: EEG, breathing, heart rate, hypnogram */
  function sleep(t, A) {
    var bands = [0.18, 0.4, 0.62, 0.84], amp = Math.min(40, H * 0.045);
    // EEG: small fast waves with slow spindles
    line(0.07 * A); x.beginPath();
    for (var i = 0; i <= W; i += 3) {
      var u = i + t * 14, sp = Math.max(0, Math.sin(u * 0.004)) ;
      var y = H * bands[0] + amp * 0.35 * (Math.sin(u * 0.09) * 0.5 + Math.sin(u * 0.23 + 1.3) * 0.3 + Math.sin(u * 0.041) * 0.6) * (0.6 + sp * sp * sp * 1.2);
      i ? x.lineTo(i, y) : x.moveTo(i, y);
    }
    x.stroke();
    // breathing: one slow wave, about 5 s a breath
    line(0.06 * A, AMB); x.beginPath();
    for (i = 0; i <= W; i += 4) {
      y = H * bands[1] + amp * Math.sin((i + t * 30) * 0.012);
      i ? x.lineTo(i, y) : x.moveTo(i, y);
    }
    x.stroke();
    // heart rate: a quiet ECG-like beat
    line(0.06 * A); x.beginPath();
    var per = 120;
    for (i = 0; i <= W; i += 2) {
      var ph = ((i + t * 40) % per) / per, v = 0;
      if (ph > 0.42 && ph < 0.46) v = -(ph - 0.42) / 0.04;
      else if (ph >= 0.46 && ph < 0.5) v = -1 + (ph - 0.46) / 0.04 * 1.4;
      else if (ph >= 0.5 && ph < 0.53) v = 0.4 - (ph - 0.5) / 0.03 * 0.4;
      else if (ph > 0.62 && ph < 0.75) v = -0.12 * Math.sin((ph - 0.62) / 0.13 * Math.PI);
      y = H * bands[2] + amp * 0.8 * v;
      i ? x.lineTo(i, y) : x.moveTo(i, y);
    }
    x.stroke();
    // hypnogram: steps between wake, REM and three depths
    line(0.07 * A); x.beginPath();
    var levels = [0, 2, 3, 4, 3, 2, 1, 2, 4, 3, 1, 0, 2, 3, 2, 1], sw = 64, off = (t * 6) % (sw * levels.length);
    for (i = -sw; i <= W + sw; i += sw) {
      var idx = Math.floor(((i + off) / sw) % levels.length + levels.length) % levels.length;
      var yy = H * bands[3] - amp * 0.9 + levels[idx] * amp * 0.45, xx = i - (off % sw);
      if (i === -sw) x.moveTo(xx, yy); else x.lineTo(xx, yy);
      x.lineTo(xx + sw, yy);
    }
    x.stroke();
  }

  /* hardware: circuit traces with a travelling pulse, a servo arc, a sensor grid */
  function hardware(t, A) {
    line(0.055 * A);
    traces.forEach(function (pts) {
      x.beginPath(); x.moveTo(pts[0][0], pts[0][1]);
      for (var i = 1; i < pts.length; i++) x.lineTo(pts[i][0], pts[i][1]);
      x.stroke();
    });
    x.fillStyle = 'rgba(' + GREY + ',' + 0.07 * A + ')';
    vias.forEach(function (v) { x.beginPath(); x.arc(v[0], v[1], 2.5, 0, 6.283); x.fill(); });
    // a pulse travels along a few traces
    for (var k = 0; k < Math.min(4, traces.length); k++) {
      var pts = traces[(k * 5) % traces.length], segs = pts.length - 1, f = ((t * 0.05 + k * 0.27) % 1) * segs,
          s = Math.floor(f), r = f - s, a = pts[s], b = pts[Math.min(s + 1, segs)];
      x.fillStyle = 'rgba(' + AMB + ',' + 0.16 * A + ')';
      x.beginPath(); x.arc(a[0] + (b[0] - a[0]) * r, a[1] + (b[1] - a[1]) * r, 2, 0, 6.283); x.fill();
    }
    // servo arc, sweeping slowly
    var cx = W * 0.82, cy = H * 0.78, R = Math.min(W, H) * 0.16;
    line(0.06 * A); x.beginPath(); x.arc(cx, cy, R, Math.PI * 1.05, Math.PI * 1.95); x.stroke();
    for (var d = 0; d <= 10; d++) {
      var an = Math.PI * (1.05 + 0.09 * d);
      x.beginPath(); x.moveTo(cx + Math.cos(an) * R, cy + Math.sin(an) * R); x.lineTo(cx + Math.cos(an) * (R - 8), cy + Math.sin(an) * (R - 8)); x.stroke();
    }
    var ang = Math.PI * (1.5 + 0.38 * Math.sin(t * 0.12));
    line(0.08 * A, AMB); x.beginPath(); x.moveTo(cx, cy); x.lineTo(cx + Math.cos(ang) * (R - 14), cy + Math.sin(ang) * (R - 14)); x.stroke();
    // sensor grid, a few cells breathing
    var gx = W * 0.06, gy = H * 0.16, g = 22;
    for (var i = 0; i < 8; i++) for (var j = 0; j < 5; j++) {
      var on = 0.5 + 0.5 * Math.sin(t * 0.25 + i * 0.9 + j * 1.7);
      x.fillStyle = 'rgba(' + GREY + ',' + (0.03 + 0.05 * on * on) * A + ')';
      x.fillRect(gx + i * g, gy + j * g, 2, 2);
    }
  }

  /* software: slow streams of code-like lines and packets on a bus */
  function software(t, A) {
    streams.forEach(function (st) {
      var lh = 18, off = (t * st.speed) % (lh * st.lines.length);
      for (var i = 0; i < st.lines.length; i++) {
        var L = st.lines[i]; if (L.gap) continue;
        var y = i * lh - off; if (y < -lh) y += lh * st.lines.length;
        if (y > H) continue;
        x.fillStyle = 'rgba(' + GREY + ',' + 0.05 * A + ')';
        x.fillRect(st.x + L.ind * 12, y, L.len, 1.5);
      }
    });
    var by = H * 0.5;
    line(0.05 * A); x.beginPath(); x.moveTo(0, by); x.lineTo(W, by); x.stroke();
    for (var k = 0; k < 6; k++) {
      var px = ((t * 22 + k * W / 6) % (W + 40)) - 20;
      x.fillStyle = 'rgba(' + (k % 3 ? GREY : AMB) + ',' + 0.12 * A + ')';
      x.fillRect(px, by - 3, 14, 6);
    }
  }

  var M = { sl: sleep, hw: hardware, sw: software };
  var cls = document.documentElement.className.match(/\bm-(hw|sw|sl)\b/);
  var mode = cls ? cls[1] : 'sl', prev = null, fade = 1;
  function pick() {
    if (cls) return;
    var y = scrollY + innerHeight * 0.5, m = 'sl';
    [['hardware', 'hw'], ['software', 'sw'], ['research', 'sl'], ['talks', 'sl']].forEach(function (p) {
      var el = document.getElementById(p[0]); if (el && el.offsetTop <= y) m = p[1];
    });
    if (m !== mode) { prev = mode; mode = m; fade = 0; if (still) draw(performance.now()); }
  }

  var t0 = performance.now(), last = 0, run = true;
  function draw(now) {
    var t = (now - t0) / 1000;
    x.clearRect(0, 0, W, H);
    if (prev && fade < 1) { M[prev](t, 1 - fade); fade = Math.min(1, fade + (still ? 1 : 0.04)); }
    M[mode](t, prev && fade < 1 ? fade : 1);
  }
  function loop(now) {
    if (!run) return;
    if (now - last > 42) { draw(now); last = now; }
    requestAnimationFrame(loop);
  }
  size();
  addEventListener('resize', function () { size(); if (still) draw(performance.now()); });
  addEventListener('scroll', function () { requestAnimationFrame(pick); }, { passive: true });
  document.addEventListener('visibilitychange', function () { run = !document.hidden; if (run && !still) requestAnimationFrame(loop); });
  pick();
  if (still) draw(t0); else requestAnimationFrame(loop);
})();
