import { defineStore } from 'pinia';
import { ref } from 'vue';

export type Theme = 'theme-light' | 'theme-dark' | 'theme-high-contrast';

const STORAGE_KEY = 'archive-theme';

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<Theme>(
    (localStorage.getItem(STORAGE_KEY) as Theme) || 'theme-light',
  );

  function applyTheme() {
    const html = document.documentElement;
    html.classList.remove('theme-light', 'theme-dark', 'theme-high-contrast');
    html.classList.add(theme.value);
    localStorage.setItem(STORAGE_KEY, theme.value);
  }

  function setTheme(newTheme: Theme) {
    theme.value = newTheme;
    applyTheme();
  }

  applyTheme();

  return { theme, setTheme };
});
