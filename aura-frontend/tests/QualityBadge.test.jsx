import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QualityBadge } from '../src/components/QualityBadge';

describe('QualityBadge', () => {
  it('renders FLAC badge when hasFlac is true', () => {
    render(<QualityBadge hasFlac />);
    expect(screen.getByText(/FLAC Lossless/i)).toBeInTheDocument();
  });

  it('renders FLAC badge when badge text contains FLAC', () => {
    render(<QualityBadge badge="FLAC Lossless" />);
    expect(screen.getByText(/FLAC Lossless/i)).toBeInTheDocument();
  });

  it('renders HQ 320kbps badge for YouTube engine', () => {
    render(<QualityBadge engine="youtube" />);
    expect(screen.getByText(/HQ 320kbps/i)).toBeInTheDocument();
  });

  it('renders Standard badge as a fallback', () => {
    render(<QualityBadge engine="other" />);
    expect(screen.getByText(/Standard/i)).toBeInTheDocument();
  });
});
