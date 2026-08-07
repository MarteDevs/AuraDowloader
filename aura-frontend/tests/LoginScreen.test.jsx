import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginScreen } from '../src/components/LoginScreen';
import { api } from '../src/services/api';

vi.mock('../src/services/api', () => ({
  api: {
    authStatus: vi.fn(),
    login: vi.fn(),
    checkHealth: vi.fn(),
    getSettings: vi.fn(),
    getQueue: vi.fn(),
    tokenStore: { get: vi.fn(() => ''), set: vi.fn(), clear: vi.fn() },
  },
}));

beforeEach(() => {
  api.login.mockReset();
  api.tokenStore.get.mockReturnValue('');
});

describe('LoginScreen', () => {
  it('renders the brand and form', () => {
    render(<LoginScreen onAuthenticated={() => {}} />);
    expect(screen.getByText(/Aura/)).toBeInTheDocument();
    expect(screen.getByLabelText(/token de acceso/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /entrar/i })).toBeInTheDocument();
  });

  it('submits the token and calls onAuthenticated', async () => {
    api.login.mockResolvedValueOnce(undefined);
    const onAuth = vi.fn();
    render(<LoginScreen onAuthenticated={onAuth} />);

    fireEvent.change(screen.getByLabelText(/token de acceso/i), {
      target: { value: 'my-token' },
    });
    fireEvent.click(screen.getByRole('button', { name: /entrar/i }));

    await waitFor(() => {
      expect(api.login).toHaveBeenCalledWith('my-token');
      expect(onAuth).toHaveBeenCalledOnce();
    });
  });

  it('shows an error when login fails', async () => {
    api.login.mockRejectedValueOnce(new Error('401'));
    render(<LoginScreen onAuthenticated={() => {}} />);

    fireEvent.change(screen.getByLabelText(/token de acceso/i), {
      target: { value: 'wrong' },
    });
    fireEvent.click(screen.getByRole('button', { name: /entrar/i }));

    const alert = await screen.findByRole('alert');
    expect(alert.textContent).toMatch(/token inválido/i);
  });

  it('disables the submit button when token is empty', () => {
    render(<LoginScreen onAuthenticated={() => {}} />);
    expect(screen.getByRole('button', { name: /entrar/i })).toBeDisabled();
  });

  it('enables the submit button when token has content', () => {
    render(<LoginScreen onAuthenticated={() => {}} />);
    fireEvent.change(screen.getByLabelText(/token de acceso/i), {
      target: { value: 'abc' },
    });
    expect(screen.getByRole('button', { name: /entrar/i })).not.toBeDisabled();
  });
});
