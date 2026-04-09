import { useThemeStore, type Theme } from '../stores/theme';
import { storeToRefs } from 'pinia';

export function useTheme() {
  const store = useThemeStore();
  const { theme } = storeToRefs(store);

  const themes: { value: Theme; label: string }[] = [
    { value: 'theme-light', label: 'Jasny' },
    { value: 'theme-dark', label: 'Ciemny' },
    { value: 'theme-high-contrast', label: 'Wysoki kontrast' },
  ];

  return {
    theme,
    themes,
    setTheme: store.setTheme,
  };
}
