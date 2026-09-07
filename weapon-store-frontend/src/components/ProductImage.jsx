import { useState } from "react";

export default function ProductImage({ src, name, priority = false }) {
  const [failedSource, setFailedSource] = useState(null);

  if (!src || failedSource === src) {
    return (
      <div className="product-image product-image--empty" role="img" aria-label={`${name}: нет изображения`}>
        <svg viewBox="0 0 48 48" fill="none" aria-hidden="true">
          <rect x="7" y="9" width="34" height="30" rx="6" />
          <circle cx="18" cy="20" r="3" />
          <path d="m9 35 10-9 7 6 7-7 7 8" />
        </svg>
        <span>Изображение отсутствует</span>
      </div>
    );
  }

  return (
    <div className="product-image">
      <img
        src={src}
        alt={name}
        loading={priority ? "eager" : "lazy"}
        decoding="async"
        onError={() => setFailedSource(src)}
      />
    </div>
  );
}
