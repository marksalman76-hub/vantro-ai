import React from 'react';
import { render, screen } from '@testing-library/react';
import QuickLaunchSection from '../QuickLaunchSection';

describe('QuickLaunchSection', () => {
  it('renders 6 quick-launch cards with correct labels', () => {
    render(<QuickLaunchSection />);

    // Verify all 6 labels are present
    expect(screen.getByText('Run an agent')).toBeInTheDocument();
    expect(screen.getByText('Output library')).toBeInTheDocument();
    expect(screen.getByText('Weekly report')).toBeInTheDocument();
    expect(screen.getByText('Brand profile')).toBeInTheDocument();
    expect(screen.getByText('Billing & credits')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('renders 6 links with correct hrefs', () => {
    const { container } = render(<QuickLaunchSection />);

    // Get all links
    const links = container.querySelectorAll('a');
    expect(links).toHaveLength(6);

    // Verify first two hrefs
    expect(links[0]).toHaveAttribute('href', '/dashboard/agents');
    expect(links[1]).toHaveAttribute('href', '/dashboard/library');

    // Verify all hrefs exist and are correct
    const expectedHrefs = [
      '/dashboard/agents',
      '/dashboard/library',
      '/dashboard/reports',
      '/dashboard/brand',
      '/dashboard/billing',
      '/dashboard/settings',
    ];

    links.forEach((link, index) => {
      expect(link).toHaveAttribute('href', expectedHrefs[index]);
    });
  });
});
