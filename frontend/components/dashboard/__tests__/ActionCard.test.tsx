import React from 'react';
import { render, screen } from '@testing-library/react';
import ActionCard from '../ActionCard';

describe('ActionCard', () => {
  it('renders as link with href, icon, label, desc', () => {
    render(
      <ActionCard
        href="/dashboard/analytics"
        icon="📊"
        label="Analytics"
        desc="View detailed reports"
      />
    );

    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', '/dashboard/analytics');
    expect(screen.getByText('📊')).toBeInTheDocument();
    expect(screen.getByText('Analytics')).toBeInTheDocument();
    expect(screen.getByText('View detailed reports')).toBeInTheDocument();
  });

  it('has transition-all class', () => {
    const { container } = render(
      <ActionCard
        href="/test"
        icon="🔧"
        label="Settings"
        desc="Manage preferences"
      />
    );

    const cardElement = container.querySelector('a');
    expect(cardElement).toHaveClass('transition-all');
  });

  it('has rounded-2xl, p-5 classes', () => {
    const { container } = render(
      <ActionCard
        href="/test"
        icon="⚙️"
        label="Config"
        desc="Configuration"
      />
    );

    const cardElement = container.querySelector('a');
    expect(cardElement).toHaveClass('rounded-2xl');
    expect(cardElement).toHaveClass('p-5');
  });
});
