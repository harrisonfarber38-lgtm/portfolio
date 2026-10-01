import { useEffect, useRef } from "react";

/** Modal image viewer. viewer = { images: [{src, alt, caption}], index } or null. */
export default function Lightbox({ viewer, onChange }) {
  const ref = useRef(null);

  useEffect(() => {
    const dlg = ref.current;
    if (viewer && !dlg.open) dlg.showModal();
    if (!viewer && dlg.open) dlg.close();
  }, [viewer]);

  const count = viewer?.images.length ?? 0;
  const go = (step) => onChange({ ...viewer, index: (viewer.index + step + count) % count });
  const image = viewer?.images[viewer.index];

  return (
    <dialog
      ref={ref}
      className="lightbox"
      aria-label="Image viewer"
      onClose={() => onChange(null)}
      onClick={(e) => e.target === ref.current && onChange(null)}
      onKeyDown={(e) => {
        if (e.key === "ArrowLeft") go(-1);
        if (e.key === "ArrowRight") go(1);
      }}
    >
      {image && (
        <>
          <button className="lightbox__close" aria-label="Close" onClick={() => onChange(null)}>×</button>
          {count > 1 && <button className="lightbox__nav lightbox__prev" aria-label="Previous image" onClick={() => go(-1)}>‹</button>}
          <figure>
            <img src={image.src} alt={image.alt} />
            <figcaption>{image.caption}</figcaption>
          </figure>
          {count > 1 && <button className="lightbox__nav lightbox__next" aria-label="Next image" onClick={() => go(1)}>›</button>}
        </>
      )}
    </dialog>
  );
}
