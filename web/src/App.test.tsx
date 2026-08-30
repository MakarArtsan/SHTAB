import { render, screen } from '@testing-library/react'
import { beforeEach, expect, test, vi } from 'vitest'

import App from '@/App'

beforeEach(() => {
  vi.stubGlobal(
    'fetch',
    vi.fn(() => Promise.resolve(new Response(JSON.stringify({ status: 'ok' })))),
  )
})

test('показывает название и статус связи', async () => {
  render(<App />)

  expect(screen.getByRole('heading', { name: 'ШТАБ' })).toBeInTheDocument()
  expect(await screen.findByText('Сервер отвечает')).toBeInTheDocument()
})
