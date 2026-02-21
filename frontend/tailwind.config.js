  /** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary - Deep Purple (matching BuildIQ design)
        primary: {
          50: '#F5F3FF',
          100: '#EDE9FE',
          200: '#DDD6FE',
          300: '#C4B5FD',
          400: '#A78BFA',
          500: '#7C3AED',
          600: '#6D28D9',
          700: '#5B21B6',
          800: '#4C1D95',
          900: '#3B0764',
        },
        // CTA - Vibrant Purple
        cta: {
          50: '#F5F3FF',
          100: '#EDE9FE',
          200: '#DDD6FE',
          300: '#C4B5FD',
          400: '#A78BFA',
          500: '#7C3AED',
          600: '#6D28D9',
          700: '#5B21B6',
          800: '#4C1D95',
          900: '#3B0764',
        },
        // Accent colors
        accent: {
          coral: '#FF6B6B',
          teal: '#14B8A6',
          amber: '#F59E0B',
          lavender: '#8B5CF6',
          rose: '#F43F5E',
          cyan: '#06B6D4',
          emerald: '#10B981',
        },
        // Dark nav background
        nav: {
          dark: '#1A1A2E',
          darker: '#16162A',
        },
        // Surface colors - Clean white
        surface: {
          50: '#FFFFFF',
          100: '#F9FAFB',
          200: '#F3F4F6',
          300: '#E5E7EB',
        },
        // Text colors
        text: {
          primary: '#111827',
          secondary: '#374151',
          tertiary: '#6B7280',
          muted: '#9CA3AF',
          light: '#D1D5DB',
          white: '#FFFFFF',
        },
      },
      fontFamily: {
        heading: ['Plus Jakarta Sans', 'sans-serif'],
        body: ['Plus Jakarta Sans', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        'clay': '20px',
        'blob': '30% 70% 70% 30% / 30% 30% 70% 70%',
        'glass': '24px',
      },
      boxShadow: {
        // Modern glass morphism shadows - Soft & Elevated
        'glass': '0 8px 32px rgba(0, 0, 0, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.6)',
        'glass-hover': '0 12px 40px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.7)',
        'glass-elevated': '0 20px 50px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.8)',
        // Premium glow shadows - AI Product Style
        'glow-primary': '0 0 40px rgba(99, 102, 241, 0.25), 0 0 80px rgba(99, 102, 241, 0.15)',
        'glow-cta': '0 0 40px rgba(168, 85, 247, 0.25), 0 0 80px rgba(168, 85, 247, 0.15)',
        'glow-sm': '0 0 20px rgba(99, 102, 241, 0.15)',
        // Modern card shadows - Layered depth
        'card': '0 1px 3px rgba(0, 0, 0, 0.04), 0 8px 16px rgba(0, 0, 0, 0.04)',
        'card-hover': '0 4px 12px rgba(0, 0, 0, 0.06), 0 16px 32px rgba(0, 0, 0, 0.06)',
        // Button shadows - Subtle depth
        'btn': '0 2px 8px rgba(99, 102, 241, 0.15)',
        'btn-hover': '0 4px 16px rgba(99, 102, 241, 0.25)',
        // Legacy clay shadows (kept for compatibility)
        'clay': '8px 8px 16px rgba(0, 0, 0, 0.08), -4px -4px 12px rgba(255, 255, 255, 0.9), inset 1px 1px 2px rgba(255, 255, 255, 0.5)',
        'clay-sm': '4px 4px 8px rgba(0, 0, 0, 0.06), -2px -2px 6px rgba(255, 255, 255, 0.8), inset 1px 1px 1px rgba(255, 255, 255, 0.4)',
        'clay-hover': '10px 10px 20px rgba(0, 0, 0, 0.1), -5px -5px 15px rgba(255, 255, 255, 0.95), inset 1px 1px 3px rgba(255, 255, 255, 0.6)',
        'clay-pressed': '2px 2px 4px rgba(0, 0, 0, 0.06), inset 3px 3px 6px rgba(0, 0, 0, 0.08)',
      },
      backdropBlur: {
        'glass': '20px',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'float-delayed': 'float 6s ease-in-out 3s infinite',
        'fade-up': 'fadeUp 0.6s ease-out forwards',
        'fade-up-delay-1': 'fadeUp 0.6s ease-out 0.1s forwards',
        'fade-up-delay-2': 'fadeUp 0.6s ease-out 0.2s forwards',
        'fade-up-delay-3': 'fadeUp 0.6s ease-out 0.3s forwards',
        'fade-in': 'fadeIn 0.3s ease-out forwards',
        'blob': 'blob 8s ease-in-out infinite',
        'blob-delayed': 'blob 8s ease-in-out 4s infinite',
        'chat-pop': 'chatPop 0.4s ease-out forwards',
        'pulse-soft': 'pulseSoft 3s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'slide-in': 'slideIn 0.5s ease-out forwards',
        'scale-in': 'scaleIn 0.3s ease-out forwards',
        'gradient-x': 'gradientX 3s ease infinite',
        'gradient-y': 'gradientY 3s ease infinite',
        'gradient-xy': 'gradientXY 3s ease infinite',
        'bounce-slight': 'bounceSlight 2s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'rotate-slow': 'rotateSlow 20s linear infinite',
        'diagonal-slide': 'diagonalSlide 0.8s ease-out forwards',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-12px)' },
        },
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(24px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        blob: {
          '0%, 100%': { borderRadius: '30% 70% 70% 30% / 30% 30% 70% 70%' },
          '50%': { borderRadius: '70% 30% 30% 70% / 70% 70% 30% 30%' },
        },
        chatPop: {
          '0%': { opacity: '0', transform: 'scale(0.8) translateY(10px)' },
          '100%': { opacity: '1', transform: 'scale(1) translateY(0)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.9)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        gradientX: {
          '0%, 100%': { 'background-position': '0% 50%' },
          '50%': { 'background-position': '100% 50%' },
        },
        gradientY: {
          '0%, 100%': { 'background-position': '50% 0%' },
          '50%': { 'background-position': '50% 100%' },
        },
        gradientXY: {
          '0%, 100%': { 'background-position': '0% 0%' },
          '25%': { 'background-position': '100% 0%' },
          '50%': { 'background-position': '100% 100%' },
          '75%': { 'background-position': '0% 100%' },
        },
        bounceSlight: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        glow: {
          '0%': { opacity: '0.5', 'box-shadow': '0 0 20px rgba(99, 102, 241, 0.3)' },
          '100%': { opacity: '1', 'box-shadow': '0 0 40px rgba(99, 102, 241, 0.6)' },
        },
        rotateSlow: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        diagonalSlide: {
          '0%': { opacity: '0', transform: 'translateX(-30px) translateY(-30px)' },
          '100%': { opacity: '1', transform: 'translateX(0) translateY(0)' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'glass-gradient': 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
      },
    },
  },
  plugins: [],
}
