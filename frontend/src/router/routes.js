const routes = [
  // No login: the demo opens straight on the dashboard
  { path: '/login', redirect: '/' },
  
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { path: '/prtg_detail/:infra_name', component: () => import('layouts/prtg_detail.vue') },
      { path: '/prtg_poller_history', component: () => import('pages/PrtgPollerHistory.vue') },
      { path: '/hostmonitor_report', component: () => import('pages/HostMonitorReport.vue') },
      { path: '/jkb_detail/:infra_name', component: () => import('layouts/jkb/jkb_detail.vue') },
      { path: '/jkb_poll_history', component: () => import('pages/JkbPollHistory.vue') },
      {
        path: '/host_monitor_detail_page/:infra_name/:hostmonitor_ip',
        component: () => import('pages/host_monitor_detail_page.vue')
      },
    ]
  },
  
  // Logout route
  { path: '/logout', redirect: '/' },

  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes