export const COPY_FEEDBACK_DURATION_MS = 1500;

export const copyToClipboard = async (text: string): Promise<boolean> => {
  // Prefer the async clipboard API (requires secure context).
  try {
    if (typeof navigator !== "undefined" && navigator.clipboard && typeof window !== "undefined" && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    // fallback below
  }

  // Fallback for older browsers / non-secure contexts.
  try {
    if (typeof document === "undefined") return false;

    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    textarea.style.top = "0";
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    const ok = document.execCommand?.("copy") ?? false;
    document.body.removeChild(textarea);
    return ok;
  } catch {
    return false;
  }
};
