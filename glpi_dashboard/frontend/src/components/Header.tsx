import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { Search, X, Clock, Calendar, ChevronDown } from 'lucide-react';
import { Theme, SearchResult } from '../types';
import { SimpleTechIcon } from './SimpleTechIcon';
import { useDebouncedCallback } from '../hooks/useDebounce';
import { useKeyboardNavigation, useListNavigation } from '../hooks/useKeyboardNavigation';
import { useScreenReaderAnnouncement } from '../components/accessibility/VisuallyHidden';

interface HeaderProps {
  currentTime: string;
  systemActive: boolean;
  theme: Theme;
  searchQuery: string;
  searchResults: SearchResult[];
  dateRange: { startDate: string; endDate: string };
  filterType?: string;
  availableFilterTypes?: Array<{
    key: string;
    name: string;
    description: string;
    default?: boolean;
  }>;
  onThemeChange: (theme: Theme) => void;
  onSearch: (query: string) => void;
  onNotification: (
    title: string,
    message: string,
    type: 'success' | 'error' | 'warning' | 'info'
  ) => void;
  onDateRangeChange?: (dateRange: { startDate: string; endDate: string; label: string }) => void;
  onFilterTypeChange?: (type: string) => void;
}

const themes: { value: Theme | 'professional'; label: string; icon: string }[] = [
  { value: 'light', label: 'Claro', icon: '☀️' },
  { value: 'dark', label: 'Escuro', icon: '🌙' },
  { value: 'professional', label: 'Professional', icon: '💼' },
];

// Predefined date ranges
const dateRanges = [
  { label: 'Hoje', days: 0 },
  { label: 'Últimos 7 dias', days: 7 },
  { label: 'Últimos 15 dias', days: 15 },
  { label: 'Últimos 30 dias', days: 30 },
  { label: 'Últimos 90 dias', days: 90 },
];

export const Header: React.FC<HeaderProps> = ({
  currentTime,
  // systemActive,
  theme,
  searchQuery,
  searchResults,
  dateRange,
  filterType,
  availableFilterTypes,
  onThemeChange,
  onSearch,
  onNotification,
  onDateRangeChange,
  onFilterTypeChange,
}) => {
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [showThemeSelector, setShowThemeSelector] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);

  const [customStartDate, setCustomStartDate] = useState('');
  const [customEndDate, setCustomEndDate] = useState('');

  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const themeRef = useRef<HTMLDivElement>(null);
  const dateRef = useRef<HTMLDivElement>(null);

  // Format date for display - memoized
  const formatDate = useCallback((dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit',
    });
  }, []);

  // Get date range label - memoized
  const getDateRangeLabel = useMemo(() => {
    // ✅ Verificação de segurança
    if (!dateRange || !dateRange.startDate || !dateRange.endDate) {
      return 'Selecionar período';
    }

    const start = new Date(dateRange.startDate);
    const end = new Date(dateRange.endDate);
    const diffTime = Math.abs(end.getTime() - start.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    const predefined = dateRanges.find(range => range.days === diffDays);
    if (predefined) return predefined.label;

    return `${formatDate(dateRange.startDate)} - ${formatDate(dateRange.endDate)}`;
  }, [dateRange, formatDate]);

  // Handle predefined date range selection
  const handleDateRangeSelect = useCallback(
    (days: number) => {
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - days);

      const startStr = startDate.toISOString().split('T')[0];
      const endStr = endDate.toISOString().split('T')[0];

      const range = dateRanges.find(r => r.days === days);
      const newDateRange = {
        startDate: startStr,
        endDate: endStr,
        label: range?.label || 'Período personalizado',
      };
      // console.log('📅 Header - Enviando dateRange:', newDateRange);
      onDateRangeChange?.(newDateRange);
      setShowDatePicker(false);

      onNotification('Período Atualizado', `Filtro alterado para: ${range?.label}`, 'info');
    },
    [onDateRangeChange, onNotification]
  );

  // Handle custom date range
  const handleCustomDateRange = useCallback(() => {
    if (customStartDate && customEndDate && onDateRangeChange) {
      const customDateRange = {
        startDate: customStartDate,
        endDate: customEndDate,
        label: 'Período personalizado',
      };
      // console.log('📅 Header - Enviando período personalizado:', customDateRange);
      onDateRangeChange(customDateRange);
      setShowDatePicker(false);
      onNotification('Período Personalizado', 'Período customizado aplicado', 'success');
    }
  }, [customStartDate, customEndDate, onDateRangeChange, onNotification]);

  // Search handlers with debounce (300ms)
  const debouncedSearch = useDebouncedCallback((query: string) => {
    onSearch(query);
  }, 300);

  const handleSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      debouncedSearch(e.target.value);
    },
    [debouncedSearch]
  );

  const handleSearchFocus = useCallback(() => {
    if (searchResults.length > 0) setShowSearchResults(true);
  }, [searchResults.length]);

  const handleSearchBlur = useCallback(() => {
    setTimeout(() => setShowSearchResults(false), 200);
  }, []);

  // Theme change handler
  const handleThemeChange = useCallback(
    (newTheme: Theme | 'professional') => {
      if (newTheme === 'professional') {
        setShowThemeSelector(false);
        onNotification(
          'Professional Dashboard',
          'Modo Professional Dashboard ativado! 💼',
          'success'
        );
        return;
      }

      onThemeChange(newTheme as Theme);
      setShowThemeSelector(false);
      const themeName = themes.find(t => t.value === newTheme)?.label;
      onNotification('Tema', `Alterado para ${themeName}`, 'info');
    },
    [onThemeChange, onNotification]
  );

  // Screen reader announcements
  const { announce } = useScreenReaderAnnouncement();

  // Search results navigation
  const {
    focusedIndex: searchFocusedIndex,
    handleKeyDown: handleSearchKeyDown,
    resetFocus: resetSearchFocus,
  } = useListNavigation({
    itemCount: searchResults.length,
    onSelect: index => {
      const result = searchResults[index];
      if (result) {
        announce(`Selecionado: ${result.title}`);
        // Handle search result selection
      }
    },
    isEnabled: showSearchResults,
  });

  // Theme selector navigation
  const {
    focusedIndex: themeFocusedIndex,
    handleKeyDown: handleThemeKeyDown,
    resetFocus: resetThemeFocus,
  } = useListNavigation({
    itemCount: themes.length,
    onSelect: index => {
      const selectedTheme = themes[index];
      if (selectedTheme) {
        handleThemeChange(selectedTheme.value);
        announce(`Tema alterado para ${selectedTheme.label}`);
      }
    },
    isEnabled: showThemeSelector,
  });

  // Date range navigation
  const {
    focusedIndex: dateFocusedIndex,
    handleKeyDown: handleDateKeyDown,
    resetFocus: resetDateFocus,
  } = useListNavigation({
    itemCount: dateRanges.length,
    onSelect: index => {
      const selectedRange = dateRanges[index];
      if (selectedRange) {
        handleDateRangeSelect(selectedRange.days);
        announce(`Período alterado para ${selectedRange.label}`);
      }
    },
    isEnabled: showDatePicker,
  });

  // Enhanced keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Global search shortcut
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
        announce('Campo de busca focado');
        return;
      }

      // Escape to close all dropdowns
      if (e.key === 'Escape') {
        setShowSearchResults(false);
        setShowThemeSelector(false);
        setShowDatePicker(false);
        resetSearchFocus();
        resetThemeFocus();
        resetDateFocus();
        announce('Menus fechados');
        return;
      }

      // Handle navigation in open dropdowns
      if (showSearchResults || showThemeSelector || showDatePicker) {
        // Create a minimal React.KeyboardEvent-like object
        const syntheticEvent = {
          key: e.key,
          preventDefault: () => e.preventDefault(),
          stopPropagation: () => e.stopPropagation(),
          currentTarget: e.target,
          target: e.target,
          nativeEvent: e,
        } as React.KeyboardEvent<Element>;

        if (showSearchResults) {
          handleSearchKeyDown(syntheticEvent);
        } else if (showThemeSelector) {
          handleThemeKeyDown(syntheticEvent);
        } else if (showDatePicker) {
          handleDateKeyDown(syntheticEvent);
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [
    showSearchResults,
    showThemeSelector,
    showDatePicker,
    handleSearchKeyDown,
    handleThemeKeyDown,
    handleDateKeyDown,
    resetSearchFocus,
    resetThemeFocus,
    resetDateFocus,
    announce,
  ]);

  // Click outside handlers
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSearchResults(false);
      }
      if (themeRef.current && !themeRef.current.contains(event.target as Node)) {
        setShowThemeSelector(false);
      }
      if (dateRef.current && !dateRef.current.contains(event.target as Node)) {
        setShowDatePicker(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Memoize current theme to prevent recalculation
  const currentTheme = useMemo(() => themes.find(t => t.value === theme) || themes[0], [theme]);

  // Memoize search clear handler
  const handleSearchClear = useCallback(() => {
    onSearch('');
  }, [onSearch]);

  return (
    <header
      className='h-16 flex items-center justify-between px-6 backdrop-blur-md bg-white/95 dark:bg-gray-900/95 border-b border-gray-200/50 dark:border-gray-700/50 w-full shadow-xl relative z-50'
      role='banner'
      aria-label='Cabeçalho principal do dashboard'
    >
      <div className='w-full px-6 py-4'>
        <div className='flex items-center justify-between w-full'>
          {/* ========== SEÇÃO ESQUERDA: LOGO + TÍTULO ========== */}
          <div
            className='flex items-center space-x-4 min-w-0 flex-shrink-0'
            role='group'
            aria-label='Logo e título do sistema'
          >
            <div
              className='w-11 h-11 bg-white/80 backdrop-blur-sm border border-white/90 dark:bg-white/5 dark:border-white/10 rounded-xl flex items-center justify-center hover:scale-105 transition-all duration-200 group'
              role='img'
              aria-label='Logo do sistema GLPI'
            >
              <SimpleTechIcon size={24} className='group-hover:scale-110 transition-transform' />
            </div>
            <div className='min-w-0'>
              <h1 className='text-2xl font-semibold text-gray-900 dark:text-gray-100 truncate'>
                Dashboard GLPI
              </h1>
              <p className='text-sm font-medium text-gray-600 dark:text-gray-300 truncate'>
                Departamento de Tecnologia do Estado
              </p>
            </div>
          </div>

          {/* ========== SEÇÃO CENTRO: BUSCA + FILTRO DE DATA ========== */}
          <div
            className='flex items-center space-x-6 flex-1 justify-center max-w-2xl mx-8'
            role='search'
            aria-label='Área de busca e filtros'
          >
            {/* Search Bar */}
            <div className='relative flex-1 max-w-md' ref={searchRef}>
              <div className='relative'>
                <Search className='absolute left-4 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-600 dark:text-gray-400 opacity-60' />
                <input
                  ref={inputRef}
                  type='text'
                  value={searchQuery}
                  onChange={handleSearchChange}
                  onFocus={handleSearchFocus}
                  onBlur={handleSearchBlur}
                  placeholder='Buscar chamados... (Ctrl+K)'
                  className='w-full pl-12 pr-10 py-3 rounded-xl text-sm font-medium border border-gray-200 bg-white/90 text-gray-900 dark:border-gray-600 dark:bg-gray-800/90 dark:text-gray-100 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 backdrop-blur-md transition-all'
                  aria-label='Campo de busca de chamados'
                  aria-describedby='search-help'
                  aria-expanded={showSearchResults}
                  aria-autocomplete='list'
                  aria-controls={showSearchResults ? 'search-results' : undefined}
                  role='combobox'
                />
                {searchQuery && (
                  <button
                    onClick={handleSearchClear}
                    className='absolute right-4 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-600 dark:text-gray-400 opacity-60 hover:opacity-100 transition-opacity'
                    aria-label='Limpar busca'
                    title='Limpar campo de busca'
                  >
                    <X className='w-4 h-4' />
                  </button>
                )}
                <div id='search-help' className='sr-only'>
                  Use Ctrl+K para focar no campo de busca. Use as setas para navegar pelos
                  resultados.
                </div>
              </div>

              {/* Search Results */}
              {showSearchResults && searchResults.length > 0 && (
                <div
                  id='search-results'
                  className='absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-2xl border border-gray-200 max-h-80 overflow-y-auto z-50'
                  role='listbox'
                  aria-label='Resultados da busca'
                >
                  {searchResults.map((result, index) => (
                    <button
                      key={`search-result-${index}`}
                      className={`w-full px-4 py-3 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0 transition-colors ${
                        index === searchFocusedIndex ? 'bg-blue-50 border-blue-200' : ''
                      }`}
                      role='option'
                      aria-selected={index === searchFocusedIndex}
                      tabIndex={-1}
                    >
                      <div className='text-sm font-medium text-gray-900'>{result.title}</div>
                      <div className='text-xs text-gray-500 mt-1'>{result.description}</div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Date Range Picker - FUNCIONAL */}
            <div className='relative' ref={dateRef}>
              <button
                onClick={() => setShowDatePicker(!showDatePicker)}
                className='flex items-center space-x-3 px-4 py-3 rounded-xl font-medium bg-white/90 text-gray-700 border border-gray-200 dark:bg-gray-800/80 dark:text-gray-200 dark:border-gray-600 hover:bg-white hover:text-gray-900 dark:hover:bg-gray-700/90 dark:hover:text-white transition-all backdrop-blur-md'
                aria-label='Seletor de período de datas'
                aria-expanded={showDatePicker}
                aria-controls={showDatePicker ? 'date-picker-menu' : undefined}
                aria-haspopup='menu'
              >
                <Calendar className='w-4 h-4' aria-hidden='true' />
                <span className='text-sm whitespace-nowrap'>{getDateRangeLabel}</span>
                <ChevronDown className='w-4 h-4' aria-hidden='true' />
              </button>

              {/* Date Picker Dropdown */}
              {showDatePicker && (
                <div
                  id='date-picker-menu'
                  className='absolute top-full right-0 mt-2 bg-white rounded-xl shadow-2xl border border-gray-200 py-3 min-w-80 z-50'
                  role='menu'
                  aria-label='Menu de seleção de período'
                >
                  <div className='px-4 pb-3 border-b border-gray-100'>
                    <h3 className='text-sm font-semibold text-gray-900'>Filtros de Data</h3>
                  </div>

                  {/* Filter Type Selector */}
                  {onFilterTypeChange && availableFilterTypes && (
                    <div className='px-4 py-3 border-b border-gray-100'>
                      <div className='text-xs font-medium text-gray-500 mb-2'>Tipo de Filtro</div>
                      <select
                        value={filterType || 'creation'}
                        onChange={e => onFilterTypeChange(e.target.value)}
                        className='w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500'
                      >
                        {availableFilterTypes.map(type => (
                          <option key={type.key} value={type.key}>
                            {type.name}
                          </option>
                        ))}
                      </select>
                      <div className='text-xs text-gray-400 mt-1'>
                        {
                          availableFilterTypes.find(t => t.key === (filterType || 'creation'))
                            ?.description
                        }
                      </div>
                    </div>
                  )}

                  {/* Predefined Ranges */}
                  <div className='py-2' role='group' aria-label='Períodos predefinidos'>
                    {dateRanges.map((range, index) => (
                      <button
                        key={range.days}
                        onClick={() => handleDateRangeSelect(range.days)}
                        className={`w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors text-sm text-gray-700 hover:text-gray-900 ${
                          index === dateFocusedIndex ? 'bg-blue-50 text-blue-700' : ''
                        }`}
                        role='menuitem'
                        tabIndex={-1}
                        aria-label={`Selecionar período: ${range.label}`}
                      >
                        {range.label}
                      </button>
                    ))}
                  </div>

                  {/* Custom Range */}
                  <div
                    className='border-t border-gray-100 pt-3 px-4'
                    role='group'
                    aria-label='Período personalizado'
                  >
                    <div className='text-xs font-medium text-gray-500 mb-2' id='custom-range-label'>
                      Período Personalizado
                    </div>
                    <div
                      className='grid grid-cols-2 gap-2 mb-3'
                      role='group'
                      aria-labelledby='custom-range-label'
                    >
                      <input
                        type='date'
                        value={customStartDate}
                        onChange={e => setCustomStartDate(e.target.value)}
                        className='px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500'
                        placeholder='Data inicial'
                        aria-label='Data inicial do período personalizado'
                      />
                      <input
                        type='date'
                        value={customEndDate}
                        onChange={e => setCustomEndDate(e.target.value)}
                        className='px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500'
                        placeholder='Data final'
                        aria-label='Data final do período personalizado'
                      />
                    </div>
                    <button
                      onClick={handleCustomDateRange}
                      disabled={!customStartDate || !customEndDate}
                      className='w-full px-3 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors'
                      aria-label='Aplicar período personalizado selecionado'
                    >
                      Aplicar Período
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* ========== SEÇÃO DIREITA: CONTROLES + STATUS ========== */}
          <div
            className='flex items-center space-x-4 flex-shrink-0'
            role='group'
            aria-label='Controles e informações do sistema'
          >
            {/* Theme Selector */}
            <div className='relative' ref={themeRef}>
              <button
                onClick={() => setShowThemeSelector(!showThemeSelector)}
                className='flex items-center space-x-2 px-3 py-2 rounded-xl text-sm font-medium bg-white/90 text-gray-700 border border-gray-200 dark:bg-gray-800/80 dark:text-gray-200 dark:border-gray-600 hover:bg-white hover:text-gray-900 dark:hover:bg-gray-700/90 dark:hover:text-white transition-all backdrop-blur-md'
                aria-label={`Seletor de tema. Tema atual: ${currentTheme.label}`}
                aria-expanded={showThemeSelector}
                aria-controls={showThemeSelector ? 'theme-selector-menu' : undefined}
                aria-haspopup='menu'
              >
                <span aria-hidden='true'>{currentTheme.icon}</span>
                <span>{currentTheme.label}</span>
              </button>

              {showThemeSelector && (
                <div
                  id='theme-selector-menu'
                  className='absolute top-full right-0 mt-2 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-600 py-2 min-w-40 z-50'
                  role='menu'
                  aria-label='Menu de seleção de tema'
                >
                  {themes.map((themeOption, index) => (
                    <button
                      key={themeOption.value}
                      onClick={() => handleThemeChange(themeOption.value)}
                      className={`w-full px-4 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-3 ${
                        theme === themeOption.value
                          ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/50 dark:text-blue-400'
                          : 'text-gray-700 dark:text-gray-200'
                      } ${index === themeFocusedIndex ? 'bg-gray-100 dark:bg-gray-600' : ''}`}
                      role='menuitem'
                      tabIndex={-1}
                      aria-label={`Selecionar tema ${themeOption.label}`}
                      aria-current={theme === themeOption.value ? 'true' : 'false'}
                    >
                      <span aria-hidden='true'>{themeOption.icon}</span>
                      <span className='text-sm'>{themeOption.label}</span>
                      {theme === themeOption.value && (
                        <div
                          className='ml-auto w-2 h-2 bg-blue-500 dark:bg-blue-400 rounded-full'
                          aria-hidden='true'
                        />
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Current Time */}
            <div
              className='bg-white/80 backdrop-blur-sm border border-white/90 dark:bg-white/5 dark:border-white/10 flex items-center space-x-2 text-sm px-3 py-2 rounded-xl font-mono'
              role='status'
              aria-label={`Horário atual: ${currentTime}`}
            >
              <Clock className='w-4 h-4' aria-hidden='true' />
              <span className='text-sm text-gray-600 dark:text-gray-300'>{currentTime}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
