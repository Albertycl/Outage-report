<template>
  <q-layout view="hHh lpR fFf">
    <!-- The product header. It carries the identity, the navigation and the
         signed-in user; individual pages no longer each grow their own top
         bar, so the chrome stays in one place and does not move between
         pages. -->
    <q-header class="app-header">
      <q-toolbar class="app-toolbar">
        <router-link to="/" class="app-brand">
          <BrandMark :size="30" />
          <div class="app-brand__text">
            <div class="app-brand__name">Outage Detector</div>
            <div class="app-brand__tag">Network Operations</div>
          </div>
        </router-link>

        <q-space />

        <!-- Primary navigation. Collapsed into a menu below the md breakpoint
             rather than wrapping onto a second row. -->
        <div class="app-nav gt-sm">
          <router-link
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="app-nav__link"
            :class="{ 'app-nav__link--active': isActive(item) }"
          >
            {{ item.label }}
          </router-link>
        </div>

        <q-btn flat dense round icon="menu" class="lt-md" color="white">
          <q-menu>
            <q-list style="min-width: 200px">
              <q-item
                v-for="item in navItems"
                :key="item.to"
                clickable
                v-close-popup
                :to="item.to"
              >
                <q-item-section>{{ item.label }}</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>

      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { useRoute } from "vue-router";

import BrandMark from "src/components/BrandMark.vue";

const route = useRoute();

const navItems = [
  { label: "Dashboard", to: "/", exact: true },
  { label: "HostMonitor Reports", to: "/hostmonitor_report" },
  { label: "PRTG History", to: "/prtg_poller_history" },
  { label: "JKB History", to: "/jkb_poll_history" },
];

function isActive(item) {
  return item.exact ? route.path === item.to : route.path.startsWith(item.to);
}
</script>

<style scoped>
.app-header {
  background: var(--app-header);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: none;
}

.app-toolbar {
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  height: 60px;
  padding: 0 24px;
}

@media (max-width: 599px) {
  .app-toolbar {
    padding: 0 12px;
  }
}

.app-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: #fff;
}

.app-brand__name {
  font-size: 16px;
  font-weight: 650;
  letter-spacing: -0.01em;
  line-height: 1.15;
}

.app-brand__tag {
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.5);
}

.app-nav {
  display: flex;
  align-items: center;
  gap: 4px;
}

.app-nav__link {
  padding: 7px 12px;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.68);
  text-decoration: none;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.app-nav__link:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}

/* the current page is stated once, in the nav, rather than repeated as a page
   title inside the content */
.app-nav__link--active {
  color: #fff;
  background: rgba(255, 255, 255, 0.13);
}

.app-user {
  color: #fff;
  padding: 4px 8px;
  border-radius: 8px;
}

.app-user__avatar {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--app-primary);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
}

.app-user__text {
  text-align: left;
  line-height: 1.2;
}

.app-user__name {
  font-size: 13px;
  font-weight: 600;
}

.app-user__org {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.55);
}
</style>
