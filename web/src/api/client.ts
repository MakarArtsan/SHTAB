const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export interface HealthStatus {
  status: string
  service: string
  env: string
}

/** Спрашивает у бэкенда, жив ли он. Ошибку не глотаем — её показывает вызывающий. */
export async function fetchHealth(signal?: AbortSignal): Promise<HealthStatus> {
  const response = await fetch(`${BASE_URL}/health`, { signal })
  if (!response.ok) {
    throw new Error('api недоступен')
  }
  return (await response.json()) as HealthStatus
}
