<template>
  <!-- Poller health. A pastel banner filled a whole row with colour whether or
       not anything was wrong; here the state is carried by one dot and the left
       border, so a healthy pipeline stays quiet and a stale one does not. -->
  <div class="status-strip" :class="stripClass">
    <span class="status-dot" :class="dotClass" />

    <div class="col">
      <!-- the headline doubles as the way into the run-by-run history -->
      <router-link to="/prtg_poller_history" class="status-strip__headline">
        {{ headline }}
        <q-icon name="open_in_new" size="12px" class="q-ml-xs" />
        <q-tooltip>See every poll run, its HTTP status and any errors</q-tooltip>
      </router-link>

      <!-- Per-infra detail -->
      <div class="status-strip__detail">
        <span
          v-for="infra in infras"
          :key="infra.infra_name"
          class="status-strip__infra"
        >
          <q-icon :name="infraIcon(infra)" :color="infraColor(infra)" size="14px" />
          <span class="text-weight-medium q-ml-xs">{{ infra.infra_name.toUpperCase() }}</span>
          <span class="q-ml-xs">{{ infraDetail(infra) }}</span>
          <q-tooltip v-if="infra.error_message">
            <template v-if="infra.error_message">
              <br />{{ infra.error_message }}
            </template>
          </q-tooltip>
        </span>
      </div>
    </div>

    <div class="row items-center q-gutter-xs no-wrap">
      <q-btn
        flat
        dense
        size="sm"
        icon="refresh"
        color="primary"
        :loading="isPolling"
        @click="pollNow"
      >
        <q-tooltip>Refresh the demo data</q-tooltip>
      </q-btn>
      <q-btn flat dense size="sm" icon="history" color="primary" to="/prtg_poller_history">
        <q-tooltip>Poll history</q-tooltip>
      </q-btn>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import axios from "axios";
import { useQuasar } from "quasar";

import { API_BASE_URL } from "src/config/api";

const $q = useQuasar();

// How often the panel re-reads the health endpoint. This only refreshes what is
// on screen; in this demo the rows are made-up and
// only re-stamped by the Refresh button; this panel reports their age.
const REFRESH_EVERY_MS = 60 * 1000;

const health = ref(null);
const loadError = ref(null);
const isPolling = ref(false);
let timer = null;

const infras = computed(() => health.value?.infras ?? []);

// The banner is red only when the health endpoint says so. A poll that failed
// but whose data is still inside the freshness window is amber, not red: the
// numbers on screen are still worth trusting for now.
const state = computed(() => {
  if (loadError.value) return "unreachable";
  if (!health.value) return "loading";
  if (!health.value.healthy) return "stale";
  if (infras.value.some((each) => each.status === "degraded")) return "degraded";
  return "ok";
});

const stripClass = computed(
  () =>
    ({
      ok: "status-strip--ok",
      degraded: "status-strip--degraded",
      stale: "status-strip--bad",
      unreachable: "status-strip--bad",
      loading: "",
    }[state.value])
);

const dotClass = computed(
  () =>
    ({
      ok: "status-dot--ok",
      degraded: "status-dot--degraded",
      stale: "status-dot--bad",
      unreachable: "status-dot--bad",
      loading: "",
    }[state.value])
);

const headline = computed(() => {
  if (state.value === "loading") return "Checking the PRTG alert status...";
  if (state.value === "unreachable")
    return `PRTG alert status unavailable - ${loadError.value}`;

  const every = health.value.poll_interval_minutes;
  const scheduler = health.value.scheduler_enabled
    ? `demo data (no PagerDuty call)`
    : "demo data - no real polling, Refresh re-stamps the seeded numbers";

  if (state.value === "ok") return `PRTG alerts up to date (${scheduler})`;
  if (state.value === "degraded")
    return `PRTG alerts still current, but the last poll failed (${scheduler})`;
  return `PRTG alerts may be STALE - ${health.value.problems.join("; ")}`;
});

function infraIcon(infra) {
  if (infra.status === "ok") return "check_circle";
  if (infra.status === "degraded") return "warning";
  return "error";
}

function infraColor(infra) {
  if (infra.status === "ok") return "green-7";
  if (infra.status === "degraded") return "orange-8";
  return "red-7";
}

function infraDetail(infra) {
  if (infra.status === "never_run") return "never polled";
  if (infra.status === "not_configured") return "no PagerDuty service configured";

  const count =
    infra.alert_count === null || infra.alert_count === undefined
      ? "?"
      : infra.alert_count;

  // While the poll is keeping up, when it last ran says nothing: it reads
  // "checked 0 min ago" every minute forever. It is only worth the space once
  // the answer stops being "just now", so it appears only when the poll is not
  // healthy - which is exactly when someone needs to know how old this is.
  if (state.value === "ok" && infra.status === "ok") return `${count} open`;

  const age =
    infra.age_minutes === null || infra.age_minutes === undefined
      ? "never"
      : `${infra.age_minutes} min ago`;
  return `${count} open - checked ${age}`;
}

async function fetchHealth() {
  try {
    const { data } = await axios.get(`${API_BASE_URL}/health/prtg_alerts`, {
      // the endpoint answers 503 when the poller is stale; that is a real
      // reading, not a transport failure, so accept it as a response
      validateStatus: (status) => status === 200 || status === 503,
    });
    health.value = data;
    loadError.value = null;
  } catch (err) {
    loadError.value = err.message || "backend unreachable";
    health.value = null;
  }
}

async function pollNow() {
  isPolling.value = true;
  try {
    const { data } = await axios.get(
      `${API_BASE_URL}/refresh_prtg_alerts_from_pagerduty`
    );
    const counts = data.alert_count_by_infra || {};
    const summary = Object.entries(counts)
      .map(([name, n]) => `${name.toUpperCase()}: ${n}`)
      .join(", ");
    $q.notify({
      color: data.status === "success" ? "green-7" : "orange-8",
      icon: data.status === "success" ? "check" : "warning",
      message: summary
        ? `Demo data refreshed - ${summary}`
        : "Demo data refreshed",
      timeout: 4000,
    });
  } catch (err) {
    $q.notify({
      color: "negative",
      icon: "error",
      message: `Refresh failed: ${
        err.response?.data?.message || err.message
      }`,
      timeout: 6000,
    });
  } finally {
    isPolling.value = false;
    await fetchHealth();
  }
}

onMounted(() => {
  fetchHealth();
  timer = setInterval(fetchHealth, REFRESH_EVERY_MS);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});

defineExpose({ fetchHealth });
</script>

<style scoped>
.status-strip__infra {
  display: inline-flex;
  align-items: center;
  margin-right: 16px;
}
</style>
