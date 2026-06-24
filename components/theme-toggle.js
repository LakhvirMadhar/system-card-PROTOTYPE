const THEME_STORAGE_KEY = 'system-card-theme';
const SUN_ICON = '☀';
const MOON_ICON = '☾';

function currentTheme() {
  const stored = document.documentElement.getAttribute('data-theme');
  if (stored) return stored;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_STORAGE_KEY, theme);
  document.getElementById('theme-toggle').textContent = theme === 'dark' ? SUN_ICON : MOON_ICON;
}

export function initThemeToggle() {
  applyTheme(localStorage.getItem(THEME_STORAGE_KEY) ?? currentTheme());

  document.getElementById('theme-toggle').addEventListener('click', () => {
    applyTheme(currentTheme() === 'dark' ? 'light' : 'dark');
  });
}
