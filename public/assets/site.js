(function () {
  var still = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* reveal on scroll */
  var els = document.querySelectorAll('.rv, .proj');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    els.forEach(function (el) { io.observe(el); });
  } else { els.forEach(function (el) { el.classList.add('in'); }); }

  /* GitHub links appear only when a URL is set in /assets/github.js */
  var G = window.GITHUB || {};
  document.querySelectorAll('[data-gh]').forEach(function (a) {
    var u = G[a.getAttribute('data-gh')];
    if (u) { a.href = u; a.hidden = false; }
  });

  /* liquid background: domain-warped noise in ember and amber, drawn at reduced resolution */
  var c = document.getElementById('fluid');
  if (!c) return;
  var gl = c.getContext('webgl', { antialias: false, alpha: false, powerPreference: 'low-power' });
  if (!gl) { c.remove(); return; }
  var vs = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  var fs = [
    '#ifdef GL_FRAGMENT_PRECISION_HIGH\nprecision highp float;\n#else\nprecision mediump float;\n#endif\n',
    'uniform vec2 r;uniform float t;uniform float s;',
    'float h(vec2 p){p=fract(p*vec2(.1031,.1030));p+=dot(p,p.yx+33.33);return fract((p.x+p.y)*p.x);}',
    'float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);',
    'return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}',
    'float fb(vec2 p){float v=0.,a=.5;for(int i=0;i<5;i++){v+=a*n(p);p=p*2.02+vec2(1.7,9.2);a*=.5;}return v;}',
    'void main(){vec2 uv=gl_FragCoord.xy/r;vec2 p=uv*vec2(r.x/r.y,1.)*1.4;float T=t*.05;',
    'p.y+=s*.35;',
    'vec2 q=vec2(fb(p+vec2(0.,T)),fb(p+vec2(5.2,1.3)-T));',
    'vec2 w=vec2(fb(p+3.*q+vec2(1.7,9.2)+T*.6),fb(p+3.*q+vec2(8.3,2.8)-T*.4));',
    'float f=fb(p+3.*w);',
    'vec3 bg=vec3(.071,.047,.031);vec3 ember=vec3(.42,.18,.07);vec3 amb=vec3(.98,.74,.42);vec3 plum=vec3(.22,.10,.20);',
    'float e=smoothstep(.38,.72,f);',
    'vec3 col=mix(bg,ember,e*.85);col=mix(col,plum,smoothstep(.45,.75,q.y)*.55*(1.-e));',
    'col+=amb*pow(smoothstep(.58,.82,f)*smoothstep(.4,.7,w.x),1.5)*.75;',
    'col*=.6+.4*smoothstep(1.3,.1,length(uv-vec2(.72,.7)));',
    'gl_FragColor=vec4(col,1.);}'
  ].join('');
  function sh(type, src) { var o = gl.createShader(type); gl.shaderSource(o, src); gl.compileShader(o); return o; }
  var pr = gl.createProgram();
  gl.attachShader(pr, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, fs));
  gl.linkProgram(pr);
  if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) { c.remove(); return; }
  gl.useProgram(pr);
  var b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
  var loc = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  var ur = gl.getUniformLocation(pr, 'r'), ut = gl.getUniformLocation(pr, 't'), us = gl.getUniformLocation(pr, 's');
  var scale = 0.35;
  function size() {
    c.width = Math.max(2, Math.round(innerWidth * scale)); c.height = Math.max(2, Math.round(innerHeight * scale));
    gl.viewport(0, 0, c.width, c.height);
  }
  size(); addEventListener('resize', size);
  var t0 = performance.now(), last = 0, run = true, sy = 0;
  addEventListener('scroll', function () { sy = scrollY / Math.max(1, innerHeight); }, { passive: true });
  document.addEventListener('visibilitychange', function () { run = !document.hidden; if (run && !still) requestAnimationFrame(loop); });
  function draw(now) {
    gl.uniform2f(ur, c.width, c.height); gl.uniform1f(ut, (now - t0) / 1000 + 40); gl.uniform1f(us, sy);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }
  function loop(now) {
    if (!run) return;
    if (now - last > 33) { draw(now); last = now; }
    requestAnimationFrame(loop);
  }
  if (still) { draw(performance.now()); addEventListener('scroll', function () { draw(performance.now()); }, { passive: true }); }
  else requestAnimationFrame(loop);
})();
