import { useEffect, useId, useRef } from "react";

export default function ConfirmDialog({ title, children, confirmLabel = "Удалить", busy = false,
  error = "", onConfirm, onCancel }) {
  const ref = useRef(null);
  const titleId = useId();
  const descriptionId = useId();

  useEffect(() => {
    const dialog = ref.current;
    dialog.showModal();
    return () => dialog.close();
  }, []);

  return (
    <dialog ref={ref} className="glass-panel admin-modal confirm-dialog"
      aria-labelledby={titleId} aria-describedby={descriptionId}
      onCancel={(event) => { event.preventDefault(); if (!busy) onCancel(); }}>
      <span className="admin-modal__mark" aria-hidden="true">!</span>
      <h2 id={titleId}>{title}</h2>
      <p id={descriptionId}>{children}</p>
      {error && <p className="confirm-dialog__error" role="alert">{error}</p>}
      <div>
        <button type="button" className="admin-modal__cancel" disabled={busy} onClick={onCancel}>
          Отмена
        </button>
        <button type="button" className="admin-modal__confirm" disabled={busy} onClick={onConfirm}>
          {busy ? "Подождите…" : confirmLabel}
        </button>
      </div>
    </dialog>
  );
}
