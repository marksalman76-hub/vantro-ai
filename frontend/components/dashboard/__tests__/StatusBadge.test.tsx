import React from 'react';
import { render, screen } from '@testing-library/react';
import StatusBadge from '../StatusBadge';

describe('StatusBadge', () => {
  it('renders "Ready" for "completed" status with green color', () => {
    render(<StatusBadge status="completed" />);

    const badge = screen.getByText('Ready');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveStyle({
      color: 'oklch(0.75 0.22 145)',
      backgroundColor: 'oklch(0.75 0.22 145 / 0.10)',
      border: '1px solid oklch(0.75 0.22 145 / 0.20)',
    });
  });

  it('renders "Needs your approval" for "pending_approval" status with orange color', () => {
    render(<StatusBadge status="pending_approval" />);

    const badge = screen.getByText('Needs your approval');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveStyle({
      color: 'oklch(0.75 0.18 55)',
      backgroundColor: 'oklch(0.75 0.18 55 / 0.10)',
      border: '1px solid oklch(0.75 0.18 55 / 0.20)',
    });
  });

  it('renders "Could not complete" for "failed" status with red color', () => {
    render(<StatusBadge status="failed" />);

    const badge = screen.getByText('Could not complete');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveStyle({
      color: 'oklch(0.65 0.18 25)',
      backgroundColor: 'oklch(0.65 0.18 25 / 0.10)',
      border: '1px solid oklch(0.65 0.18 25 / 0.20)',
    });
  });

  it('has pill-shaped styling with correct dimensions', () => {
    render(<StatusBadge status="completed" />);

    const badge = screen.getByText('Ready');
    expect(badge).toHaveStyle({
      borderRadius: '9999px',
      fontSize: '10px',
      padding: '2px 8px',
      fontWeight: '600',
    });
  });
});
