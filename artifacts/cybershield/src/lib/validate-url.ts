export type UrlValidationResult =
  | { valid: true; value: string }
  | { valid: false; message: string };

export function validateUrlInput(raw: string): UrlValidationResult {
  const value = raw.trim();
  if (!value || value.length > 2048 || /[\u0000-\u001f\u007f]/u.test(value)) {
    return {
      valid: false,
      message: 'Enter a web address between 1 and 2,048 characters without control characters.',
    };
  }

  const candidate = value.includes('://') ? value : `https://${value}`;
  try {
    const parsed = new URL(candidate);
    if (!['http:', 'https:'].includes(parsed.protocol) || !parsed.hostname) {
      return { valid: false, message: 'Enter a complete HTTP or HTTPS address with a hostname.' };
    }
    const host = parsed.hostname.replace(/\.$/u, '');
    const labels = host.split('.');
    if (
      host.length > 253 ||
      labels.some((label) => !label || label.length > 63)
    ) {
      return { valid: false, message: 'Check the address format and try again.' };
    }
    // Accessing .port forces URL to reject malformed values such as :99999.
    void parsed.port;
  } catch {
    return { valid: false, message: 'Enter a complete HTTP or HTTPS address with a hostname.' };
  }

  return { valid: true, value };
}
