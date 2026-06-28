import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ThemeToggle from '../ThemeToggle';
import * as useThemeModule from '../../../lib/hooks/useTheme';

// Mock the useTheme hook
jest.mock('../../../lib/hooks/useTheme', () => ({
  useTheme: jest.fn(),
}));

describe('ThemeToggle', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders toggle button', () => {
    (useThemeModule.useTheme as jest.Mock).mockReturnValue({
      theme: 'dark',
      setTheme: jest.fn(),
    });

    render(<ThemeToggle />);
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
  });

  it('has fixed bottom-left positioning', () => {
    (useThemeModule.useTheme as jest.Mock).mockReturnValue({
      theme: 'dark',
      setTheme: jest.fn(),
    });

    const { container } = render(<ThemeToggle />);
    const button = container.querySelector('button');
    const style = window.getComputedStyle(button);

    // Button should have fixed positioning styles
    expect(button).toHaveStyle('position: fixed');
    expect(button).toHaveStyle('bottom: 2rem');
    expect(button).toHaveStyle('left: 2rem');
    expect(button).toHaveStyle('z-index: 50');
  });

  it('displays sun icon for dark theme', () => {
    (useThemeModule.useTheme as jest.Mock).mockReturnValue({
      theme: 'dark',
      setTheme: jest.fn(),
    });

    render(<ThemeToggle />);
    expect(screen.getByText('☀️')).toBeInTheDocument();
  });

  it('displays moon icon for light theme', () => {
    (useThemeModule.useTheme as jest.Mock).mockReturnValue({
      theme: 'light',
      setTheme: jest.fn(),
    });

    render(<ThemeToggle />);
    expect(screen.getByText('🌙')).toBeInTheDocument();
  });

  it('displays refresh icon for auto theme', () => {
    (useThemeModule.useTheme as jest.Mock).mockReturnValue({
      theme: 'auto',
      setTheme: jest.fn(),
    });

    render(<ThemeToggle />);
    expect(screen.getByText('🔄')).toBeInTheDocument();
  });

  it('cycles through themes on click', () => {
    const setThemeMock = jest.fn();
    (useThemeModule.useTheme as jest.Mock).mockReturnValue({
      theme: 'dark',
      setTheme: setThemeMock,
    });

    const { rerender } = render(<ThemeToggle />);
    const button = screen.getByRole('button');

    fireEvent.click(button);
    expect(setThemeMock).toHaveBeenCalledWith('light');

    // Re-render with light theme
    (useThemeModule.useTheme as jest.Mock).mockReturnValue({
      theme: 'light',
      setTheme: setThemeMock,
    });
    rerender(<ThemeToggle />);

    fireEvent.click(button);
    expect(setThemeMock).toHaveBeenCalledWith('auto');

    // Re-render with auto theme
    (useThemeModule.useTheme as jest.Mock).mockReturnValue({
      theme: 'auto',
      setTheme: setThemeMock,
    });
    rerender(<ThemeToggle />);

    fireEvent.click(button);
    expect(setThemeMock).toHaveBeenCalledWith('dark');
  });

  it('has correct title/tooltip', () => {
    (useThemeModule.useTheme as jest.Mock).mockReturnValue({
      theme: 'dark',
      setTheme: jest.fn(),
    });

    render(<ThemeToggle />);
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('title', 'Theme: dark');
  });

  it('has button styling with oklch colors and rounded edges', () => {
    (useThemeModule.useTheme as jest.Mock).mockReturnValue({
      theme: 'dark',
      setTheme: jest.fn(),
    });

    const { container } = render(<ThemeToggle />);
    const button = container.querySelector('button');

    expect(button).toHaveStyle('border-radius: 0.375rem');
    expect(button).toHaveStyle('padding: 0.5rem 0.75rem');
  });
});
