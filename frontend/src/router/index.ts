import { createRouter, createWebHistory } from 'vue-router';

const SITE_NAME = 'Cyfrowe Archiwum Społecznościowe';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
      meta: { title: SITE_NAME },
    },
    {
      path: '/browse',
      name: 'browse',
      component: () => import('../views/BrowseView.vue'),
      meta: { title: `Przeglądaj – ${SITE_NAME}` },
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('../views/SearchView.vue'),
      meta: { title: `Szukaj – ${SITE_NAME}` },
    },
    {
      path: '/photos/:id',
      name: 'photo-detail',
      component: () => import('../views/PhotoDetailView.vue'),
      props: true,
      meta: { title: `Zdjęcie – ${SITE_NAME}` },
    },
    {
      path: '/upload',
      name: 'upload',
      component: () => import('../views/UploadView.vue'),
      meta: { requiresAuth: true, title: `Dodaj zdjęcie – ${SITE_NAME}` },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { title: `Logowanie – ${SITE_NAME}` },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { title: `Rejestracja – ${SITE_NAME}` },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true, title: `Mój profil – ${SITE_NAME}` },
    },
    {
      path: '/admin',
      name: 'admin-dashboard',
      component: () => import('../views/admin/DashboardView.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
        title: `Panel admina – ${SITE_NAME}`,
      },
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: () => import('../views/admin/UsersView.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
        title: `Użytkownicy – ${SITE_NAME}`,
      },
    },
    {
      path: '/admin/moderation',
      name: 'admin-moderation',
      component: () => import('../views/admin/ModerationView.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
        title: `Moderacja – ${SITE_NAME}`,
      },
    },
    {
      path: '/admin/hierarchy',
      name: 'admin-hierarchy',
      component: () => import('../views/admin/HierarchyView.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
        title: `Lokalizacje – ${SITE_NAME}`,
      },
    },
  ],
});

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token');

  if (to.meta.requiresAuth && !token) {
    next({ name: 'login', query: { redirect: to.fullPath } });
    return;
  }

  if (to.meta.title) {
    document.title = to.meta.title as string;
  }

  next();
});

export default router;
