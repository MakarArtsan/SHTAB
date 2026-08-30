import type { Config } from 'tailwindcss'
import animate from 'tailwindcss-animate'

// Цвета заданы CSS-переменными в src/index.css — так их понимает shadcn/ui.
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        border: 'hsl(var(--border))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
      },
      // Минимальная целевая область нажатия — 44 px, требование мобильного экрана.
      spacing: { touch: '2.75rem' },
    },
  },
  plugins: [animate],
} satisfies Config
