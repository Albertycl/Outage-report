<template>
  <!-- Reader health. Same strip as the pollers: colour only when a read has
       actually gone wrong, rather than a filled banner either way. -->
  <div class="status-strip" :class="isHealthy ? 'status-strip--ok' : 'status-strip--bad'">
    <span class="status-dot" :class="isHealthy ? 'status-dot--ok' : 'status-dot--bad'" />

    <div class="col">
      <!-- the headline doubles as the way into the reading-by-reading log -->
      <router-link to="/hostmonitor_report" class="status-strip__headline">
        {{ headline }}
        <q-icon name="open_in_new" size="12px" class="q-ml-xs" />
        <q-tooltip>See every read of the reports, and any errors</q-tooltip>
      </router-link>

      <!-- Per-infra detail: how fresh, and the LTM / not-LTM split -->
      <div class="status-strip__detail">
        <span
          v-for="infra in infras"
          :key="infra.infra_name"
          class="status-strip__infra"
        >
          <q-icon :name="infraIcon(infra)" :color="infraColor(infra)" size="14px" />
          <span class="text-weight-medium q-ml-xs">
            {{ infra.infra_name.toUpperCase() }}
          </span>
          <span class="q-ml-xs">{{ infraDetail(infra) }}</span>
          <q-tooltip v-if="infra.report_path || infra.last_run?.error_message">
            {{ infra.report_path }}
            <template v-if="infra.last_run && infra.last_run.error_message">
              <br />{{ infra.last_run.error_message }}
            </template>
          </q-tooltip>
        </span>
      </div>
    </div>

    <q-btn
      flat
      dense
      size="sm"
      icon="refresh"
      color="primary"
      :loading="isReading"
      @click="readNow"
    >
      <q-tooltip>Read the reports now</q-tooltip>
    </q-btn>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import axios from "axios";

import { API_BASE_URL } from "src/config/api";

// The backend reads the files once a minute; match it rather than poll faster
// than there is anything new to see.
const RELOAD_EVERY_MS = 60 * 1000;

const health = ref({});
const isReading = ref(false);
const loadFailed = ref(false);
let timer = null;

const infras = computed(() => health.value.infras || []);

const headline = computed(() => {
  if (loadFailed.value) return "HostMonitor reports: cannot reach the backend";
  if (!health.value.infras) return "HostMonitor reports: checking...";
  if (health.value.healthy) {
    return "HostMonitor demo data (no real report is read)";
  }
  // the first problem is the useful one; the rest are in the page behind it
  return `HostMonitor reports: ${health.value.problems[0]}`;
});

const isHealthy = computed(() => !loadFailed.value && health.value.healthy);


function infraIcon(infra) {
  return (
    {
      ok: "check_circle",
      degraded: "error_outline",
      stale: "history_toggle_off",
      error: "cancel",
      never_run: "help_outline",
      not_configured: "settings",
    }[infra.state] || "help_outline"
  );
}

function infraColor(infra) {
  return (
    {
      ok: "green-7",
      degraded: "orange-8",
      stale: "orange-8",
      error: "red-7",
      never_run: "grey-6",
      not_configured: "blue-7",
    }[infra.state] || "grey-6"
  );
}

function infraDetail(infra) {
  if (infra.state === "not_configured") return "no report file configured";
  if (!infra.last_run) return "never read";

  const run = infra.last_run;
  // a failed read is the whole story; the counts on screen are the older ones
  if (run.status !== "ok") {
    return `read failed ${infra.age_minutes === null ? "" : `(showing data ${infra.age_minutes} min old)`}`;
  }
  const detail = `${run.ltm_alert_count ?? 0} LTM / ${run.not_ltm_alert_count ?? 0} not LTM alerting`;

  // While the reads are keeping up, how long ago the last one was says
  // nothing - it is always "0 min ago". It appears only once the read is no
  // longer healthy, which is when its age is the point.
  if (isHealthy.value && infra.state === "ok") return detail;
  return `${detail}, ${infra.age_minutes} min ago`;
}

async function load() {
  try {
    // an unhealthy reader answers 503, which is the state we most want to
    // show, so it must not be treated as a failed request
    const { data } = await axios.get(`${API_BASE_URL}/health/hostmonitor_report`, {
      validateStatus: (status) => status === 200 || status === 503,
    });
    health.value = data;
    loadFailed.value = false;
  } catch {
    loadFailed.value = true;
  }
}

async function readNow() {
  isReading.value = true;
  try {
    await axios.get(`${API_BASE_URL}/refresh_hostmonitor_report`, {
      validateStatus: () => true,
    });
    await load();
  } finally {
    isReading.value = false;
  }
}

onMounted(() => {
  load();
  timer = setInterval(load, RELOAD_EVERY_MS);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>

<style scoped>
.status-strip__infra {
  display: inline-flex;
  align-items: center;
  margin-right: 16px;
}
</style>
