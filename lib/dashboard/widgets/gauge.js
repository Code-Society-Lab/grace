(() => {
  "use strict";

  const RADIUS = 70;
  const CENTER_X = 90;
  const CENTER_Y = 84;
  const STROKE = 14;
  const SVG_NS = "http://www.w3.org/2000/svg";

  const point = (angleDeg, radius) => {
    const rad = (angleDeg * Math.PI) / 180;
    return [CENTER_X + radius * Math.cos(rad), CENTER_Y - radius * Math.sin(rad)];
  };

  // Maps a value to its angle on the arc: min sits at 180deg (left), max at
  // 0deg (right), sweeping up through 90deg (top).
  const angleFor = (value, min, max) => {
    const clamped = Math.min(max, Math.max(min, value));
    return 180 - (180 * (clamped - min)) / (max - min);
  };

  const arcPath = (fromAngle, toAngle) => {
    const [x1, y1] = point(fromAngle, RADIUS);
    const [x2, y2] = point(toAngle, RADIUS);
    const largeArc = fromAngle - toAngle > 180 ? 1 : 0;
    return `M ${x1} ${y1} A ${RADIUS} ${RADIUS} 0 ${largeArc} 1 ${x2} ${y2}`;
  };

  const arc = (className) => {
    const path = document.createElementNS(SVG_NS, "path");
    path.setAttribute("class", className);
    path.setAttribute("fill", "none");
    path.setAttribute("stroke-width", STROKE);
    path.setAttribute("stroke-linecap", "round");
    return path;
  };

  const format = (value) =>
    value == null ? "—" : Number.isInteger(value) ? String(value) : value.toFixed(1);

  const paint = (state, payload) => {
    const { min, max, warning_at: warningAt, critical_at: criticalAt, value, unit } = payload;
    const warnAngle = angleFor(warningAt, min, max);
    const critAngle = angleFor(criticalAt, min, max);

    state.good.setAttribute("d", arcPath(180, warnAngle));
    state.warn.setAttribute("d", arcPath(warnAngle, critAngle));
    state.bad.setAttribute("d", arcPath(critAngle, 0));

    state.needle.style.display = value == null ? "none" : "";

    if (value != null) {
      const [x, y] = point(angleFor(value, min, max), RADIUS - STROKE);
      state.needle.setAttribute("x2", x);
      state.needle.setAttribute("y2", y);
    }

    state.readout.textContent = format(value);
    state.unit.textContent = value == null ? "" : (unit ?? "");
  };

  window.Dachshund.widget("gauge", {
    mount(card, payload) {
      const container = card.querySelector(".card-content");
      container.classList.add("gauge");

      const svg = document.createElementNS(SVG_NS, "svg");
      svg.setAttribute("viewBox", "0 0 180 100");
      svg.setAttribute("class", "gauge-arc");

      const good = arc("gauge-zone gauge-zone-good");
      const warn = arc("gauge-zone gauge-zone-warning");
      const bad = arc("gauge-zone gauge-zone-critical");

      const needle = document.createElementNS(SVG_NS, "line");
      needle.setAttribute("class", "gauge-needle");
      needle.setAttribute("x1", CENTER_X);
      needle.setAttribute("y1", CENTER_Y);

      svg.append(good, warn, bad, needle);

      const reading = document.createElement("div");
      reading.className = "gauge-reading";
      const readout = document.createElement("span");
      readout.className = "gauge-value";
      const unit = document.createElement("span");
      unit.className = "gauge-unit";
      reading.append(readout, unit);

      container.append(svg, reading);

      const state = { good, warn, bad, needle, readout, unit };
      paint(state, payload);

      return state;
    },
    replace: paint,
  });
})();
