import { render, screen, waitFor } from '@testing-library/react';
import { expect, it, vi, beforeEach, describe } from 'vitest';
import React from 'react';
import App from './App';

// Mock de los componentes 3D que requieren WebGL (no disponible en JSDOM)
vi.mock('./components/Nebula3DBackground', () => ({
  default: () => <div data-testid="nebula-3d-scene" />
}));

describe('Nebula Frontend Integration Test', () => {
  beforeEach(() => {
    // Mock del fetch global
    vi.stubGlobal('fetch', vi.fn());
  });

  it('debe mostrar la pantalla de carga al inicio', () => {
    fetch.mockResolvedValue({
      json: () => new Promise(() => {}), // Nunca resuelve para ver el loader
    });
    render(<App />);
    expect(screen.getByText(/Initializing Semantic Observatory/i)).toBeDefined();
  });

  it('debe renderizar el dashboard con datos de telemetría reales', async () => {
    const mockEvents = [
      {
        event_id: 'test-uuid',
        timestamp: new Date().toISOString(),
        action_text: 'Refactor de motor cuático',
        category: 'Work',
        state: 'Friction',
        final_score: 0.85,
        physics_params: { identity_snapshot: { drift_delta: 0.1234 } }
      }
    ];
    
    const mockMasses = {
      field_masses: { engineering: 1.0 },
      connections: {},
      dominant: 'engineering',
      field_colors: { engineering: '#00D1FF' }
    };

    // Simulamos las respuestas de los endpoints de la API
    fetch.mockImplementation((url) => {
      if (url.includes('/events')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ events: mockEvents }) });
      }
      if (url.includes('/field-mass')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(mockMasses) });
      }
      return Promise.reject(new Error('Endpoint no mockeado'));
    });

    render(<App />);

    // Esperar a que el loading desaparezca
    await waitFor(() => {
      expect(screen.queryByText(/Initializing/i)).toBeNull();
    });

    // Verificaciones de UI
    expect(screen.getByText('Nebula')).toBeDefined();
    expect(screen.getByText('Telemetry Online')).toBeDefined();
    expect(screen.getByText('0.1234')).toBeDefined(); // Valor de drift_delta
    expect(screen.getByText('Refactor de motor cuático')).toBeDefined();
    expect(screen.getByTestId('nebula-3d-scene')).toBeDefined();
  });
});