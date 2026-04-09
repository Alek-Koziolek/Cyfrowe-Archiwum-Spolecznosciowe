import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User } from '../types/user';
import * as authApi from '../api/auth';

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const loading = ref(false);

  const isAuthenticated = computed(() => !!user.value);
  const isAdmin = computed(() => user.value?.role === 'admin');
  const isContributor = computed(() => !!user.value && !user.value.is_blocked);

  async function register(
    email: string,
    password: string,
    displayName: string,
  ) {
    const tokens = await authApi.register({
      email,
      password,
      display_name: displayName,
    });
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    user.value = await authApi.getMe();
  }

  async function login(email: string, password: string) {
    const tokens = await authApi.login({ email, password });
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    user.value = await authApi.getMe();
  }

  function logout() {
    user.value = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  async function fetchUser() {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    try {
      loading.value = true;
      user.value = await authApi.getMe();
    } catch {
      logout();
    } finally {
      loading.value = false;
    }
  }

  return {
    user,
    loading,
    isAuthenticated,
    isAdmin,
    isContributor,
    register,
    login,
    logout,
    fetchUser,
  };
});
