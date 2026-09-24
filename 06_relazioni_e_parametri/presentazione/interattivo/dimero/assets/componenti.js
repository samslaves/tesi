/*
 * componenti.js — pezzi di interfaccia riusati dalle 4 pagine:
 *   - arrowSVG / renderAmps : ampiezze complesse come frecce nel piano
 *   - LineChart             : grafico a linee generico (assi, griglia, tracce,
 *                             linee verticali/orizzontali di riferimento, punti)
 * Nessuna libreria esterna: solo SVG costruito a mano, nello stesso stile
 * grafico del documento 4 originale.
 */
(function (global) {
  "use strict";

  function arrowSVG(re, im, color, opts) {
    opts = opts || {};
    const R = opts.r || 26, size = opts.size || 58, sc = R / (opts.scale || 0.75);
    const x = re * sc, y = -im * sc;
    const cx = size / 2, cy = size / 2;
    const m = Math.hypot(re, im);
    const head = m > 0.02 ? `<circle cx="${(cx+x).toFixed(1)}" cy="${(cy+y).toFixed(1)}" r="2.6" fill="${color}"/>` : "";
    return `<svg viewBox="0 0 ${size} ${size}" width="${size}" height="${size}">
      <circle cx="${cx}" cy="${cy}" r="${R}" fill="none" stroke="#D5DEE8" stroke-width="1"/>
      <line x1="${cx-R*1.08}" y1="${cy}" x2="${cx+R*1.08}" y2="${cy}" stroke="#D5DEE8" stroke-width="1"/>
      <line x1="${cx}" y1="${cy-R*1.08}" x2="${cx}" y2="${cy+R*1.08}" stroke="#D5DEE8" stroke-width="1"/>
      <line x1="${cx}" y1="${cy}" x2="${(cx+x).toFixed(1)}" y2="${(cy+y).toFixed(1)}" stroke="${color}" stroke-width="2"/>
      ${head}</svg>`;
  }

  function renderAmps(el, re, im, kets, color, emptyMsg) {
    if (!re) {
      el.innerHTML = `<div style="grid-column:1/-1;font-family:var(--mono);font-size:12px;color:#8496A8;padding:12px 0">${emptyMsg || "ramo non presente"}</div>`;
      return;
    }
    im = im || re.map(() => 0);
    el.innerHTML = kets.map((k, n) => {
      const r = re[n], i = im[n], m = Math.hypot(r, i);
      return `<div class="ampcell"><div class="lbl">${k}</div>${arrowSVG(r, i, color)}<div class="num">${m.toFixed(3)}</div></div>`;
    }).join("");
  }

  // ------------------------------------------------------------- LineChart
  // opts = { w,h, margin:{l,r,t,b}, xDomain:[a,b], yDomain:[a,b], logY,
  //          xTicks:[...], yTicks:[...], xLabel, yLabel,
  //          series:[{x:[...],y:[...],color,dash,width}],
  //          vlines:[{x,color,dash,label}], points:[{x,y,color,r}] }
  function LineChart(svgEl, opts) {
    const W = opts.w || 700, H = opts.h || 300;
    const m = Object.assign({ l: 48, r: 16, t: 12, b: 30 }, opts.margin || {});
    const pw = W - m.l - m.r, ph = H - m.t - m.b;
    const [x0, x1] = opts.xDomain, [y0, y1] = opts.yDomain;
    const X = opts.logX
      ? v => m.l + pw * (Math.log10(v) - Math.log10(x0)) / (Math.log10(x1) - Math.log10(x0))
      : v => m.l + pw * (v - x0) / (x1 - x0);
    const Y = opts.logY
      ? v => m.t + ph * (1 - (Math.log10(v) - Math.log10(y0)) / (Math.log10(y1) - Math.log10(y0)))
      : v => m.t + ph * (1 - (v - y0) / (y1 - y0));

    let s = "";
    // griglia + tick
    (opts.yTicks || []).forEach(v => {
      s += `<line x1="${m.l}" y1="${Y(v)}" x2="${W-m.r}" y2="${Y(v)}" stroke="${Math.abs(v)<1e-12?'#8FA2B5':'#D5DEE8'}" stroke-width="1"/>`;
      s += `<text x="${m.l-7}" y="${Y(v)+4}" text-anchor="end" font-family="ui-monospace,monospace" font-size="10" fill="#5C7288">${opts.yFmt ? opts.yFmt(v) : v}</text>`;
    });
    (opts.xTicks || []).forEach(v => {
      s += `<text x="${X(v)}" y="${H-m.b+16}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="10" fill="#5C7288">${opts.xFmt ? opts.xFmt(v) : v}</text>`;
    });
    s += `<line x1="${m.l}" y1="${m.t}" x2="${m.l}" y2="${H-m.b}" stroke="#8FA2B5" stroke-width="1"/>`;
    s += `<line x1="${m.l}" y1="${H-m.b}" x2="${W-m.r}" y2="${H-m.b}" stroke="#8FA2B5" stroke-width="1"/>`;

    // vlines di riferimento (es. incrocio a B/J=2)
    (opts.vlines || []).forEach(v => {
      s += `<line x1="${X(v.x)}" y1="${m.t}" x2="${X(v.x)}" y2="${H-m.b}" stroke="${v.color||'#8FA2B5'}" stroke-width="${v.width||1.2}" stroke-dasharray="${v.dash||'3 3'}"/>`;
    });

    // serie
    (opts.series || []).forEach(sr => {
      const pts = sr.x.map((xv, i) => `${X(xv).toFixed(2)},${Y(sr.y[i]).toFixed(2)}`).join(" ");
      s += `<polyline points="${pts}" fill="none" stroke="${sr.color}" stroke-width="${sr.width||1.8}" ${sr.dash?`stroke-dasharray="${sr.dash}"`:""} opacity="${sr.opacity!==undefined?sr.opacity:1}"/>`;
    });

    // punti singoli (marcatori)
    (opts.points || []).forEach(p => {
      s += `<circle cx="${X(p.x).toFixed(2)}" cy="${Y(p.y).toFixed(2)}" r="${p.r||4}" fill="${p.color}" stroke="#fff" stroke-width="1.3"/>`;
    });

    // etichette degli assi: grandezza + unita' di misura (o "adimensionale" se non ne ha una fisica)
    if (opts.xLabel) {
      s += `<text x="${m.l+pw/2}" y="${H-3}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="11" fill="#5C7288">${opts.xLabel}</text>`;
    }
    if (opts.yLabel) {
      const cx = 12, cy = m.t + ph / 2;
      s += `<text x="${cx}" y="${cy}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="11" fill="#5C7288" transform="rotate(-90 ${cx} ${cy})">${opts.yLabel}</text>`;
    }

    svgEl.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svgEl.innerHTML = s;
  }

  // ------------------------------------------------------------ CircuitDiagram
  // Disegna un circuito a N fili a partire da una lista generica di porte.
  // Ogni porta e' uno di questi 4 tipi:
  //   {kind:"BOX",  wire, label}                       -- porta a un filo (X, H, Ry...)
  //   {kind:"CTRL", control, target, open, targetLabel, showAsCnot} -- controllata
  //   {kind:"DOTS", wires:[i,j]}                        -- simmetrica coi soli pallini (CZ)
  //   {kind:"SPAN", wires:[...], label}                 -- box che copre piu' fili (RBS, U(t)...)
  // highlightIndex evidenzia la porta corrente (per l'animazione passo-passo);
  // undefined/-1 per non evidenziare nulla.
  function CircuitDiagram(svgEl, steps, opts) {
    opts = opts || {};
    const nWires = opts.nWires || 2;
    const wireLabels = opts.wireLabels || Array.from({ length: nWires }, (_, i) => `q${i}`);
    const slot = 76, padL = 56, padR = 20, padTop = 30, padBot = 20;
    const wireGap = 58;
    const yW = Array.from({ length: nWires }, (_, i) => padTop + i * wireGap);
    const W = padL + Math.max(steps.length, 1) * slot + padR;
    const H = padTop + (nWires - 1) * wireGap + padBot;
    const hi = opts.highlightIndex;

    let s = "";
    wireLabels.forEach((lab, i) => {
      s += `<line x1="${padL-26}" y1="${yW[i]}" x2="${W-padR+14}" y2="${yW[i]}" stroke="#8FA2B5" stroke-width="1.4"/>`;
      s += `<text x="${padL-32}" y="${yW[i]+4}" text-anchor="end" font-family="ui-monospace,monospace" font-size="11.5" fill="#14273A">${lab}</text>`;
    });

    steps.forEach((st, i) => {
      const cx = padL + i * slot + slot / 2;
      const active = i === hi;
      const done = hi !== undefined && hi !== null && hi >= 0 && i < hi;
      const col = active ? "#A8560C" : (done ? "#0E7C86" : "#5C7288");
      if (active) {
        s += `<rect x="${cx-slot/2+3}" y="${padTop-22}" width="${slot-6}" height="${(nWires-1)*wireGap+44}" fill="#FCEEDD"/>`;
      }
      if (st.kind === "DOTS") {
        const ys = st.wires.map(w => yW[w]);
        s += `<line x1="${cx}" y1="${Math.min(...ys)}" x2="${cx}" y2="${Math.max(...ys)}" stroke="${col}" stroke-width="2"/>`;
        st.wires.forEach(w => s += `<circle cx="${cx}" cy="${yW[w]}" r="5" fill="${col}"/>`);
      } else if (st.kind === "CTRL") {
        const cyC = yW[st.control], cyT = yW[st.target];
        s += `<line x1="${cx}" y1="${cyC}" x2="${cx}" y2="${cyT}" stroke="${col}" stroke-width="2"/>`;
        s += st.open
          ? `<circle cx="${cx}" cy="${cyC}" r="5" fill="#fff" stroke="${col}" stroke-width="2"/>`
          : `<circle cx="${cx}" cy="${cyC}" r="5" fill="${col}"/>`;
        if (st.showAsCnot) {
          s += `<circle cx="${cx}" cy="${cyT}" r="11" fill="#fff" stroke="${col}" stroke-width="2"/>`;
          s += `<line x1="${cx-8}" y1="${cyT}" x2="${cx+8}" y2="${cyT}" stroke="${col}" stroke-width="2"/>`;
          s += `<line x1="${cx}" y1="${cyT-8}" x2="${cx}" y2="${cyT+8}" stroke="${col}" stroke-width="2"/>`;
        } else {
          s += `<rect x="${cx-18}" y="${cyT-16}" width="36" height="32" fill="#fff" stroke="${col}" stroke-width="1.6"/>`;
          s += `<text x="${cx}" y="${cyT+4}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="12" fill="${col}">${st.targetLabel}</text>`;
        }
      } else if (st.kind === "SPAN") {
        const ys = st.wires.map(w => yW[w]);
        const y0 = Math.min(...ys), y1 = Math.max(...ys);
        s += `<rect x="${cx-28}" y="${y0-17}" width="56" height="${y1-y0+34}" fill="#fff" stroke="${col}" stroke-width="1.6"/>`;
        s += `<text x="${cx}" y="${(y0+y1)/2+4}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="10.5" fill="${col}">${st.label}</text>`;
      } else {
        // BOX: porta a un filo solo
        const cy = yW[st.wire];
        const wBox = (st.label || "").length > 2 ? 54 : 30;
        s += `<rect x="${cx-wBox/2}" y="${cy-16}" width="${wBox}" height="32" fill="#fff" stroke="${col}" stroke-width="1.6"/>`;
        s += `<text x="${cx}" y="${cy+4}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="${wBox>40?10:12}" fill="${col}">${st.label}</text>`;
      }
    });

    svgEl.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svgEl.innerHTML = s;
  }

  const Componenti = { arrowSVG, renderAmps, LineChart, CircuitDiagram };
  if (typeof module !== "undefined" && module.exports) module.exports = Componenti;
  else global.Componenti = Componenti;
})(typeof window !== "undefined" ? window : globalThis);
