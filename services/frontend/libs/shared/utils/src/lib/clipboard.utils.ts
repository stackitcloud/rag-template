export const COPY_FEEDBACK_DURATION_MS = 1500;

const tryExecCommandCopy = (value: string): boolean => {
  try {
    if (typeof document === "undefined") return false;
    if (!document.body) return false;

    const previousActiveElement =
      typeof document.activeElement !== "undefined"
        ? (document.activeElement as HTMLElement | null)
        : null;
    const selection = document.getSelection?.();
    const previousRange =
      selection && selection.rangeCount > 0 ? selection.getRangeAt(0) : null;

    const textarea = document.createElement("textarea");
    textarea.value = value;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.top = "0";
    textarea.style.left = "0";
    textarea.style.opacity = "0";
    textarea.style.pointerEvents = "none";
    textarea.style.width = "1px";
    textarea.style.height = "1px";
    document.body.appendChild(textarea);

    try {
      try {
        textarea.focus({ preventScroll: true } as FocusOptions);
      } catch {
        textarea.focus();
      }

      textarea.select();
      try {
        textarea.setSelectionRange(0, textarea.value.length);
      } catch {
        // ignore
      }

      return document.execCommand?.("copy") ?? false;
    } finally {
      try {
        document.body.removeChild(textarea);
      } catch {
        // ignore
      }

      try {
        previousActiveElement?.focus?.({ preventScroll: true } as FocusOptions);
      } catch {
        previousActiveElement?.focus?.();
      }

      if (selection && previousRange) {
        selection.removeAllRanges();
        selection.addRange(previousRange);
      }
    }
  } catch {
    return false;
  }
};

export const copyToClipboard = async (text: string): Promise<boolean> => {
  const value = text ?? "";
  if (!value) return false;

  // Prefer a synchronous fallback first to keep user-activation in stricter browsers.
  if (tryExecCommandCopy(value)) return true;

  // Then try the async clipboard API (availability/permissions vary by browser).
  try {
    if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(value);
      return true;
    }
  } catch {
    // ignore
  }

  return false;
};
