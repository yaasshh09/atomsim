const L_LETTERS = "spdfghik";

export function isValidState(n: number, l: number, m: number): boolean {
  return (
    Number.isInteger(n) &&
    Number.isInteger(l) &&
    Number.isInteger(m) &&
    n >= 1 &&
    l >= 0 &&
    l < n &&
    Math.abs(m) <= l
  );
}

export function stateLabel(n: number, l: number, m: number): string {
  const letter = L_LETTERS[l] ?? `(l=${l})`;
  return `${n}${letter} (m = ${m})`;
}

export function clampState(n: number, l: number, m: number): { n: number; l: number; m: number } {
  const cn = Math.max(1, Math.round(n));
  const cl = Math.min(Math.max(0, Math.round(l)), cn - 1);
  const cm = Math.min(Math.max(Math.round(m), -cl), cl);
  // + 0 normalizes -0 (from -cl when cl === 0) to +0
  return { n: cn, l: cl, m: cm + 0 };
}
