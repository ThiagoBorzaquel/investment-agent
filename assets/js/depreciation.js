export function projectResaleValue(purchasePrice, years, curve) {
  const key = String(years);
  const factor = curve[key] ?? estimateFactorFromCurve(curve, years);
  return purchasePrice * factor;
}

function estimateFactorFromCurve(curve, years) {
  const knownYears = Object.keys(curve).map(Number).sort((a, b) => a - b);
  if (knownYears.length === 0) return 0.45;
  if (years <= knownYears[0]) return curve[knownYears[0]];
  if (years >= knownYears[knownYears.length - 1]) {
    return Math.max(0.18, curve[knownYears[knownYears.length - 1]] - 0.04 * (years - knownYears[knownYears.length - 1]));
  }

  for (let i = 0; i < knownYears.length - 1; i += 1) {
    const y1 = knownYears[i];
    const y2 = knownYears[i + 1];
    if (years >= y1 && years <= y2) {
      const f1 = curve[y1];
      const f2 = curve[y2];
      const t = (years - y1) / (y2 - y1);
      return f1 + t * (f2 - f1);
    }
  }

  return 0.45;
}

export function expectedBatteryCost(batteryCost, probability, years) {
  const horizonFactor = years >= 8 ? 1 : years / 8;
  return batteryCost * probability * horizonFactor;
}
