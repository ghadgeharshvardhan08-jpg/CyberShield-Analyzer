import { describe, expect, it } from 'vitest';

import { validateUrlInput } from './validate-url';

describe('validateUrlInput', () => {
  it('accepts a hostname without a scheme for backend normalization', () => {
    expect(validateUrlInput('  example.com/account  ')).toEqual({
      valid: true,
      value: 'example.com/account',
    });
  });

  it('rejects non-web schemes, malformed hosts, control characters, and oversized input', () => {
    expect(validateUrlInput('javascript:alert(1)').valid).toBe(false);
    expect(validateUrlInput('https://')).toMatchObject({ valid: false });
    expect(validateUrlInput('https://bad..example/path')).toMatchObject({ valid: false });
    expect(validateUrlInput('https://example.com/\npath')).toMatchObject({ valid: false });
    expect(validateUrlInput(`https://${'a'.repeat(2050)}.com`)).toMatchObject({ valid: false });
  });
});
