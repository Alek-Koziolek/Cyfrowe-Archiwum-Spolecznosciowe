import { useAuthStore } from '../stores/auth';
import { storeToRefs } from 'pinia';

export function useAuth() {
  const store = useAuthStore();
  const { user, isAuthenticated, isAdmin, isContributor, loading } =
    storeToRefs(store);

  return {
    user,
    isAuthenticated,
    isAdmin,
    isContributor,
    loading,
    register: store.register,
    login: store.login,
    logout: store.logout,
    fetchUser: store.fetchUser,
  };
}
