import { useEffect, useState } from 'react'

import { fetchHealth } from '@/api/client'

type ApiState = 'checking' | 'online' | 'offline'

const API_LABEL: Record<ApiState, string> = {
  checking: 'Проверяем связь с сервером',
  online: 'Сервер отвечает',
  offline: 'Сервер пока не отвечает',
}

export default function App() {
  const [apiState, setApiState] = useState<ApiState>('checking')

  useEffect(() => {
    const controller = new AbortController()
    fetchHealth(controller.signal)
      .then(() => setApiState('online'))
      .catch(() => setApiState('offline'))
    return () => controller.abort()
  }, [])

  return (
    <main className="mx-auto flex min-h-dvh max-w-md flex-col justify-between p-4">
      <div>
        <h1 className="text-2xl font-semibold">ШТАБ</h1>
        <p className="mt-2 text-muted-foreground">
          Координация наблюдателей. Каркас развёрнут, экраны появятся дальше по плану.
        </p>
      </div>

      <p className="rounded-lg border border-border bg-muted p-4 text-sm" role="status">
        {API_LABEL[apiState]}
      </p>
    </main>
  )
}
