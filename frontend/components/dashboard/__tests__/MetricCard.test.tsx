import React from 'react';
import { render, screen } from '@testing-library/react';
import MetricCard from '../MetricCard';

describe('MetricCard', () => {
  it('renders label, value, and sub when all provided', () => {
    render(
      <MetricCard
        label="Total Revenue"
        value={15420}
        sub="Last 30 days"
      />
    );

    expect(screen.getByText('Total Revenue')).toBeInTheDocument();
    expect(screen.getByText('15420')).toBeInTheDocument();
    expect(screen.getByText('Last 30 days')).toBeInTheDocument();
  });

  it('renders without sub when not provided', () => {
    render(
      <MetricCard
        label="Total Users"
        value={1250}
      />
    );

    expect(screen.getByText('Total Users')).toBeInTheDocument();
    expect(screen.getByText('1250')).toBeInTheDocument();
  });

  it('applies color class to value when provided', () => {
    const { container } = render(
      <MetricCard
        label="Status"
        value="Active"
        color="oklch(0.70 0.2 100)"
      />
    );

    const valueElement = screen.getByText('Active');
    expect(valueElement).toHaveStyle({ color: 'oklch(0.70 0.2 100)' });
  });
});
