import React from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme, Theme } from '../contexts/ThemeContext';
import { motion, AnimatePresence } from 'framer-motion';

interface ThemeToggleProps {
  className?: string;
  showLabel?: boolean;
}

const ThemeToggle: React.FC<ThemeToggleProps> = ({ className = '', showLabel = false }) => {
  const { theme, actualTheme, setTheme } = useTheme();

  const themes: { value: Theme; icon: React.ReactNode; label: string }[] = [
    { value: 'light', icon: <Sun size={16} />, label: 'Claro' },
    { value: 'dark', icon: <Moon size={16} />, label: 'Escuro' },
    { value: 'system', icon: <Monitor size={16} />, label: 'Sistema' },
  ];

  const currentThemeIndex = themes.findIndex(t => t.value === theme);
  const nextTheme = themes[(currentThemeIndex + 1) % themes.length];

  const handleToggle = () => {
    setTheme(nextTheme.value);
  };

  return (
    <motion.button
      onClick={handleToggle}
      className={`
        relative flex items-center gap-2 px-3 py-2 rounded-lg
        bg-white hover:bg-gray-50 dark:bg-gray-800 dark:hover:bg-gray-700
        border border-gray-200 dark:border-gray-700
        text-gray-700 dark:text-gray-300
        transition-all duration-200 ease-in-out
        focus:outline-none focus:ring-2 focus:ring-blue-500/50
        ${className}
      `}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      title={`Tema atual: ${themes[currentThemeIndex].label}. Clique para alternar para: ${nextTheme.label}`}
      aria-label={`Alternar tema. Tema atual: ${themes[currentThemeIndex].label}`}
    >
      <AnimatePresence mode='wait'>
        <motion.div
          key={theme}
          initial={{ opacity: 0, rotate: -90 }}
          animate={{ opacity: 1, rotate: 0 }}
          exit={{ opacity: 0, rotate: 90 }}
          transition={{ duration: 0.2 }}
          className='flex items-center'
        >
          {themes[currentThemeIndex].icon}
        </motion.div>
      </AnimatePresence>

      {showLabel && (
        <AnimatePresence mode='wait'>
          <motion.span
            key={theme}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 10 }}
            transition={{ duration: 0.2 }}
            className='text-sm font-medium'
          >
            {themes[currentThemeIndex].label}
          </motion.span>
        </AnimatePresence>
      )}

      {/* Indicador visual do tema do sistema */}
      {theme === 'system' && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className={`
            absolute -top-1 -right-1 w-3 h-3 rounded-full
            ${actualTheme === 'dark' ? 'bg-gray-800' : 'bg-yellow-400'}
            border-2 border-white dark:border-gray-900
          `}
          title={`Sistema detectado: ${actualTheme === 'dark' ? 'Escuro' : 'Claro'}`}
        />
      )}
    </motion.button>
  );
};

export default React.memo(ThemeToggle);
