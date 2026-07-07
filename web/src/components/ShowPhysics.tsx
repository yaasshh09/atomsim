import katex from "katex";
import { PHYSICS_CONTENT } from "../physics/content";
import { useAppStore } from "../state/store";

function MathBlock({ tex }: { tex: string }) {
  // KaTeX renders our own static strings only — no user input reaches it.
  const html = katex.renderToString(tex, { displayMode: true, throwOnError: false });
  return <div className="math" dangerouslySetInnerHTML={{ __html: html }} />;
}

export function ShowPhysics() {
  const view = useAppStore((s) => s.view);
  const content = PHYSICS_CONTENT[view];
  return (
    <details className="physics">
      <summary>Show the physics</summary>
      <h3>{content.title}</h3>
      {content.blocks.map((b) => (
        <div key={b.tex}>
          <MathBlock tex={b.tex} />
          <p className="physics-note">{b.note}</p>
        </div>
      ))}
    </details>
  );
}
