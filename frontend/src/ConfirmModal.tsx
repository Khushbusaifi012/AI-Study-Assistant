import { useEffect } from "react";

interface ConfirmModalProps {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  danger?: boolean;
  success?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmModal({
  open,
  title,
  message,
  confirmLabel = "OK",
  cancelLabel = "Cancel",
  danger = false,
  success = false,
  onConfirm,
  onCancel,
}: ConfirmModalProps) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onCancel();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onCancel]);

  if (!open) return null;

  const handleBackdrop = () => {
    if (success) onConfirm();
    else onCancel();
  };

  return (
    <div className="modal-overlay" role="presentation" onClick={handleBackdrop}>
      <div
        className={`modal-card${success ? " modal-card--success" : ""}`}
        role="alertdialog"
        aria-labelledby="modal-title"
        aria-describedby="modal-desc"
        onClick={(e) => e.stopPropagation()}
      >
        {success && <div className="modal-icon success">✓</div>}
        <h3 id="modal-title" className="modal-title">
          {title}
        </h3>
        <p id="modal-desc" className="modal-message">
          {message}
        </p>
        <div className="modal-actions">
          {!success && (
            <button type="button" className="modal-btn cancel" onClick={onCancel}>
              {cancelLabel}
            </button>
          )}
          <button
            type="button"
            className={`modal-btn confirm${danger ? " danger" : ""}${
              success ? " success" : ""
            }`}
            onClick={onConfirm}
            autoFocus
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
