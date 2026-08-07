import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Header } from '../src/components/Header';

function renderWithRouter(ui, initialRoute = '/') {
  return render(<MemoryRouter initialEntries={[initialRoute]}>{ui}</MemoryRouter>);
}

describe('Header', () => {
  it('renders the brand', () => {
    renderWithRouter(<Header isOnline queueCount={0} onOpenSettings={() => {}} onToggleQueue={() => {}} />);
    expect(screen.getByText(/Aura/)).toBeInTheDocument();
  });

  it('shows online status', () => {
    renderWithRouter(<Header isOnline queueCount={0} onOpenSettings={() => {}} onToggleQueue={() => {}} />);
    expect(screen.getByText(/Motor Conectado/i)).toBeInTheDocument();
  });

  it('shows offline status when isOnline=false', () => {
    renderWithRouter(<Header isOnline={false} queueCount={0} onOpenSettings={() => {}} onToggleQueue={() => {}} />);
    expect(screen.getByText(/Sin Conexión/i)).toBeInTheDocument();
  });

  it('shows queue count badge when queueCount > 0', () => {
    renderWithRouter(<Header isOnline queueCount={3} onOpenSettings={() => {}} onToggleQueue={() => {}} />);
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('hides queue count badge when queueCount is 0', () => {
    renderWithRouter(<Header isOnline queueCount={0} onOpenSettings={() => {}} onToggleQueue={() => {}} />);
    expect(screen.queryByText('0')).not.toBeInTheDocument();
  });

  it('calls onToggleQueue when downloads button clicked', () => {
    const onToggle = vi.fn();
    renderWithRouter(<Header isOnline queueCount={2} onOpenSettings={() => {}} onToggleQueue={onToggle} />);
    fireEvent.click(screen.getByLabelText(/cola de descargas/i));
    expect(onToggle).toHaveBeenCalledOnce();
  });

  it('calls onOpenSettings when settings button clicked', () => {
    const onOpen = vi.fn();
    renderWithRouter(<Header isOnline queueCount={0} onOpenSettings={onOpen} onToggleQueue={() => {}} />);
    fireEvent.click(screen.getByLabelText(/configuración/i));
    expect(onOpen).toHaveBeenCalledOnce();
  });

  it('renders navigation links to all pages', () => {
    renderWithRouter(<Header isOnline queueCount={0} onOpenSettings={() => {}} onToggleQueue={() => {}} />);
    expect(screen.getByRole('link', { name: /buscar/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /biblioteca/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /favoritos/i })).toBeInTheDocument();
  });
});
