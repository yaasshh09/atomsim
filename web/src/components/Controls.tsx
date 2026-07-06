import { useAppStore } from "../state/store";

const N_CHOICES = [1, 2, 3, 4, 5, 6];
const COUNT_CHOICES = [10_000, 50_000, 100_000, 250_000];

export function Controls() {
  const { n, l, m, count, status, progress, error, setQuantumNumbers, setCount, sample } =
    useAppStore();
  const lChoices = Array.from({ length: n }, (_, i) => i);
  const mChoices = Array.from({ length: 2 * l + 1 }, (_, i) => i - l);
  return (
    <aside className="panel">
      <h2>State</h2>
      <label>
        n
        <select value={n} onChange={(e) => setQuantumNumbers(Number(e.target.value), l, m)}>
          {N_CHOICES.map((v) => (
            <option key={v} value={v}>
              {v}
            </option>
          ))}
        </select>
      </label>
      <label>
        l
        <select value={l} onChange={(e) => setQuantumNumbers(n, Number(e.target.value), m)}>
          {lChoices.map((v) => (
            <option key={v} value={v}>
              {v}
            </option>
          ))}
        </select>
      </label>
      <label>
        m
        <select value={m} onChange={(e) => setQuantumNumbers(n, l, Number(e.target.value))}>
          {mChoices.map((v) => (
            <option key={v} value={v}>
              {v}
            </option>
          ))}
        </select>
      </label>
      <h2>Sampling</h2>
      <label>
        points
        <select value={count} onChange={(e) => setCount(Number(e.target.value))}>
          {COUNT_CHOICES.map((v) => (
            <option key={v} value={v}>
              {v.toLocaleString()}
            </option>
          ))}
        </select>
      </label>
      <button
        type="button"
        className="primary"
        disabled={status === "sampling"}
        onClick={() => void sample()}
      >
        {status === "sampling" ? `Sampling ${(progress * 100).toFixed(0)}%` : "Sample"}
      </button>
      {status === "error" && <p className="error">{error}</p>}
    </aside>
  );
}
