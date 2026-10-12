(function () {
  var frogs = Array.prototype.slice.call(document.querySelectorAll('.frog'));
  var btn = document.getElementById('sound'), label = btn.querySelector('span');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var ctx = null, master = null, on = false;

  function rnd(a, b) { return a + Math.random() * (b - a); }

  function noiseBuffer(brown) {
    var len = ctx.sampleRate * 4, buf = ctx.createBuffer(1, len, ctx.sampleRate), d = buf.getChannelData(0), last = 0;
    for (var i = 0; i < len; i++) {
      var w = Math.random() * 2 - 1;
      if (brown) { last = (last + 0.02 * w) / 1.02; d[i] = last * 3.5; } else d[i] = w;
    }
    return buf;
  }

  function loopNoise(brown, type, freq, q, gain) {
    var src = ctx.createBufferSource(); src.buffer = noiseBuffer(brown); src.loop = true;
    var f = ctx.createBiquadFilter(); f.type = type; f.frequency.value = freq; f.Q.value = q;
    var g = ctx.createGain(); g.gain.value = gain;
    src.connect(f); f.connect(g); g.connect(master); src.start();
    return g;
  }

  // Slow random swell on a gain node (wind through trees, water lapping)
  function swell(g, base, depth, period) {
    (function step() {
      if (!ctx) return;
      g.gain.linearRampToValueAtTime(base + Math.random() * depth, ctx.currentTime + period);
      setTimeout(step, period * 1000);
    })();
  }

  var scene = document.body.getAttribute('data-scene') || 'pond';

  // Tropical birds: quick whistled phrases from random directions
  function birds() {
    (function call() {
      if (!ctx) return;
      var t = ctx.currentTime + 0.05, pan = ctx.createStereoPanner(), g = ctx.createGain(), o = ctx.createOscillator();
      pan.pan.value = rnd(-0.9, 0.9); o.type = 'sine';
      o.connect(g); g.connect(pan); pan.connect(master); g.gain.value = 0;
      var notes = 2 + Math.floor(Math.random() * 4), base = rnd(1400, 3200), dur = rnd(0.07, 0.16);
      for (var i = 0; i < notes; i++) {
        var s = t + i * (dur + 0.05);
        o.frequency.setValueAtTime(base * rnd(0.8, 1.1), s);
        o.frequency.exponentialRampToValueAtTime(base * rnd(1.2, 1.6), s + dur);
        g.gain.setValueAtTime(0, s); g.gain.linearRampToValueAtTime(0.05, s + 0.02); g.gain.linearRampToValueAtTime(0, s + dur);
      }
      o.start(t); o.stop(t + notes * (dur + 0.05) + 0.1);
      setTimeout(call, rnd(1500, 5000));
    })();
    // Low, hollow call of a distant bird
    (function hoo() {
      if (!ctx) return;
      var t = ctx.currentTime + 0.05, o = ctx.createOscillator(), g = ctx.createGain(), pan = ctx.createStereoPanner();
      pan.pan.value = rnd(-1, 1); o.frequency.value = rnd(480, 620);
      o.connect(g); g.connect(pan); pan.connect(master); g.gain.value = 0;
      for (var i = 0; i < 3; i++) {
        g.gain.setValueAtTime(0, t + i * 0.45); g.gain.linearRampToValueAtTime(0.04, t + i * 0.45 + 0.08); g.gain.linearRampToValueAtTime(0, t + i * 0.45 + 0.32);
      }
      o.start(t); o.stop(t + 1.5);
      setTimeout(hoo, rnd(7000, 14000));
    })();
  }

  // Insect buzz: band-limited noise with a fast tremolo
  function insects() {
    var g = loopNoise(false, 'bandpass', 5200, 9, 0.0);
    var lfo = ctx.createOscillator(), depth = ctx.createGain();
    lfo.frequency.value = 38; depth.gain.value = 0.025; lfo.connect(depth); depth.connect(g.gain); lfo.start();
    swell(g, 0.01, 0.03, 4);
  }

  function startAmbience() {
    if (scene === 'jungle') {
      swell(loopNoise(true, 'lowpass', 900, 0.4, 0.5), 0.4, 0.15, 2);     // waterfall rumble
      swell(loopNoise(false, 'highpass', 3000, 0.5, 0.01), 0.008, 0.008, 2); // spray hiss
      birds(); insects();
    }
    swell(loopNoise(true, 'lowpass', 420, 0.5, 0.35), 0.2, 0.25, 3);      // wind & distant water
    swell(loopNoise(false, 'bandpass', 2400, 1.2, 0.012), 0.006, 0.014, 1.2); // stream trickle
    // Crickets: short chirps of 3 pulses
    [[4400, -0.6], [4700, 0.5], [4100, 0.1]].forEach(function (c) {
      var pan = ctx.createStereoPanner(); pan.pan.value = c[1]; pan.connect(master);
      (function chirp() {
        if (!ctx) return;
        var t = ctx.currentTime + 0.05, o = ctx.createOscillator(), g = ctx.createGain();
        o.frequency.value = c[0]; o.connect(g); g.connect(pan); g.gain.value = 0;
        for (var i = 0; i < 3; i++) {
          g.gain.setValueAtTime(0, t + i * 0.045);
          g.gain.linearRampToValueAtTime(0.018, t + i * 0.045 + 0.01);
          g.gain.linearRampToValueAtTime(0, t + i * 0.045 + 0.035);
        }
        o.start(t); o.stop(t + 0.2);
        setTimeout(chirp, rnd(600, 1100));
      })();
    });
  }

  // Frog call: buzzy pulses through a throat-like bandpass. Big frogs are deeper.
  function croakSound(frog) {
    if (!on || !ctx) return;
    var size = parseFloat(frog.dataset.s), x = parseFloat(frog.dataset.x);
    var pan = ctx.createStereoPanner(); pan.pan.value = Math.max(-1, Math.min(1, (x - 800) / 800));
    var vol = ctx.createGain(); vol.gain.value = 0.25 + size * 0.25;
    var f = ctx.createBiquadFilter(); f.type = 'bandpass'; f.Q.value = 3;
    var o = ctx.createOscillator(); o.type = 'sawtooth';
    var g = ctx.createGain(); g.gain.value = 0;
    o.connect(f); f.connect(g); g.connect(vol); vol.connect(pan); pan.connect(master);
    var t = ctx.currentTime + 0.02, base = size > 1.1 ? rnd(70, 95) : rnd(140, 220);
    f.frequency.value = base * 4;
    var pulses = size > 1.1 ? 1 : 2, end = t;
    for (var p = 0; p < pulses; p++) {
      var s = t + p * 0.22, len = size > 1.1 ? 0.55 : 0.16;
      o.frequency.setValueAtTime(base * 1.15, s);
      o.frequency.exponentialRampToValueAtTime(base * 0.85, s + len);
      // rapid flutter gives the rough "rrr" texture
      for (var k = 0; k < len / 0.025; k++) {
        g.gain.setValueAtTime(0.5, s + k * 0.025);
        g.gain.linearRampToValueAtTime(0.08, s + k * 0.025 + 0.018);
      }
      g.gain.setValueAtTime(0, s + len);
      end = s + len;
    }
    o.start(t); o.stop(end + 0.05);
  }

  function animate(el, cls, ms) {
    el.classList.remove(cls); void el.getBBox(); el.classList.add(cls);
    setTimeout(function () { el.classList.remove(cls); }, ms);
  }

  (function frogLife() {
    var frog = frogs[Math.floor(Math.random() * frogs.length)];
    var hopper = frog.querySelector('.hopper'), sac = frog.querySelector('.sac');
    if (Math.random() < 0.45) {
      if (!reduce) animate(hopper, 'hop', 800);
      setTimeout(function () { if (!reduce) animate(sac, 'croak', 950); croakSound(frog); }, 800);
    } else {
      if (!reduce) animate(sac, 'croak', 950);
      croakSound(frog);
    }
    setTimeout(frogLife, rnd(900, 3200));
  })();

  btn.addEventListener('click', function () {
    if (!ctx) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) { label.textContent = 'no audio'; return; }
      ctx = new AC();
      master = ctx.createGain(); master.gain.value = 0; master.connect(ctx.destination);
      startAmbience();
    }
    on = !on;
    if (on) ctx.resume();
    master.gain.cancelScheduledValues(ctx.currentTime);
    master.gain.setValueAtTime(master.gain.value, ctx.currentTime);
    master.gain.linearRampToValueAtTime(on ? 0.6 : 0, ctx.currentTime + 1);
    btn.setAttribute('aria-pressed', on);
    label.textContent = on ? 'sound off' : 'sound on';
  });
})();
