import { thumbnailUrl } from "../api/client";
import type { Basis } from "../api/client";
import { galleryStates } from "../lib/gallery";
import { THUMBNAIL_LIBERTY } from "../lib/liberties";
import { stateLabel } from "../lib/quantum";
import { useAppStore } from "../state/store";
import { Badge } from "./Badge";

export function GalleryStrip() {
  const { n, l, m, system, basis, setQuantumNumbers } = useAppStore();
  return (
    <div className="gallery">
      <div className="gallery-head">
        <span>n = {n} states</span>
        <Badge provenance={THUMBNAIL_LIBERTY} />
      </div>
      <div className="gallery-scroll">
        {galleryStates(n).map((s) => {
          const active = s.l === l && s.m === m;
          return (
            <button
              key={`${s.l},${s.m}`}
              type="button"
              className={active ? "thumb thumb-active" : "thumb"}
              title={stateLabel(s.n, s.l, s.m)}
              onClick={() => setQuantumNumbers(s.n, s.l, s.m)}
            >
              <img
                src={thumbnailUrl(s.n, s.l, s.m, system, basis as Basis, 96)}
                alt={stateLabel(s.n, s.l, s.m)}
                width={72}
                height={72}
                loading="lazy"
              />
              <span>{stateLabel(s.n, s.l, s.m)}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
