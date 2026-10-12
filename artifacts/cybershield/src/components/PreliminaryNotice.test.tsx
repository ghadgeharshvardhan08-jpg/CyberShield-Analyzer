import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it } from 'vitest';

import { PreliminaryNotice } from './PreliminaryNotice';

afterEach(cleanup);

describe('PreliminaryNotice', () => {
  it('clearly communicates that a low score is not a safety guarantee', () => {
    render(<PreliminaryNotice />);

    expect(screen.getByRole('note', { name: 'Assessment limitation' })).toHaveTextContent(
      /not a guarantee/i,
    );
    expect(screen.getByRole('note')).toHaveTextContent(/not proof of safety/i);
  });
});
