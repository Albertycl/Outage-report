<template>
  <!-- Poller health. A pastel banner filled a whole row with colour whether or
       not anything was wrong; here the state is carried by one dot and the left
       border, so a healthy pipeline stays quiet and a stale one does not. -->
  <div class="status-strip" :class="stripClass">
    <span class="status-dot" :class="dotClass" />

    <div class="col">
      <!-- the headline doubles as the way into the run-by-run history -->
      <router-link to="/jkb_poll_history" class="status-strip__headline">
        {{ headline }}
        <q-icon name="open_in_new" size="12px" class="q-ml-xs" />
        <q-tooltip>See every JKB run, each step's HTTP status and any errors</q-tooltip>
      </router-link>

      <!-- Per-infra detail -->
      <div class="status-strip__detail">
        <span
          v-for="infra in infras"
          :key="infra.infra_name"
          class="status-strip__infra"
        >
          <q-icon :name="infraIcon(infra)" :color="infraColor(infra)" size="14px" />
          <span class="text-weight-medium q-ml-xs">{{ infra.infra_name }}</span>
          <span class="q-ml-xs">{{ infraDetail(infra) }}</span>
          <q-tooltip v-if="infra.error_message">
            {{ infra.error_message }}
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
        <q-tooltip>Run the JKB pipeline now</q-tooltip>
      </q-btn>
      <q-btn flat dense size="sm" icon="history" color="primary" to="/jkb_poll_history">
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
// on screen; the backend scheduler runs the pipeline on its own interval and
// this panel reports what that scheduler last managed to do.
const REFRESH_EVERY_MS = 60 * 1000;

const emit = defineEmits(["polled"]);

const health = ref(null);
const loadError = ref(null);
const isPolling = ref(false);
let timer = null;

const infras = computed(() => health.value?.infras ?? []);

// Red only when the health endpoint says so. A run that failed but whose data
// is still inside the freshness window is amber, not red: the numbers on screen
// are still worth trusting for now.
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
  if (state.value === "loading") return "Checking the JKB pipeline...";
  if (state.value === "unreachable")
    return `JKB pipeline status unavailable - ${loadError.value}`;

  const every = health.value.poll_interval_minutes;
  const scheduler = health.value.scheduler_enabled
    ? `running every ${every} min`
    : "demo data - no real polling, Refresh re-stamps the seeded numbers";

  if (state.value === "ok") return `JKB alerts up to date (${scheduler})`;
  if (state.value === "degraded")
    return `JKB alerts still current, but the last run failed (${scheduler})`;
  return `JKB alerts may be STALE - ${health.value.problems.join("; ")}`;
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
  if (infra.status === "never_run") return "never run";
  // a zero alert count off zero sensors is an unknown, not a healthy infra
  if (infra.status === "no_sensors") return "no sensors classified into it";

  const count =
    infra.alert_count === null || infra.alert_count === undefined
      ? "?"
      : infra.alert_count;
  const detail = `${count} alerting of ${infra.sensor_count} sensors`;

  // While the run is keeping up, when it last ran says nothing: it reads
  // "checked 0 min ago" every minute forever. It earns its space only once the
  // answer stops being "just now", so it appears only when the feed is not
  // healthy - which is exactly when someone needs to know how old this is.
  if (state.value === "ok" && infra.status === "ok") return detail;

  const age =
    infra.age_minutes === null || infra.age_minutes === undefined
      ? "never"
      : `${infra.age_minutes} min ago`;
  return `${detail} - checked ${age}`;
}

async function fetchHealth() {
  try {
    const { data } = await axios.get(`${API_BASE_URL}/health/jkb`, {
      // the endpoint answers 503 when the feed is stale; that is a real
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
    const { data } = await axios.get(`${API_BASE_URL}/refresh_all_jkb`, {
      // a failed run is a result worth reporting, not an exception to swallow
      validateStatus: (status) => status < 600,
    });
    const counts = data.alert_count_by_infra || {};
    const summary = Object.entries(counts)
      .map(([name, n]) => `${name}: ${n}`)
      .join(", ");
    const ok = data.status === "success";
    $q.notify({
      color: ok ? "green-7" : "negative",
      icon: ok ? "check" : "error",
      message: ok
        ? `JKB refreshed${summary ? ` - ${summary}` : ""}`
        : `JKB run failed at ${data.failed_at}: ${data.message || "see the history page"}`,
      timeout: ok ? 4000 : 8000,
    });
  } catch (err) {
    $q.notify({
      color: "negative",
      icon: "error",
      message: `JKB refresh failed: ${err.response?.data?.message || err.message}`,
      timeout: 6000,
    });
  } finally {
    isPolling.value = false;
    await fetchHealth();
    // the cards read their own endpoint, so tell them the numbers moved
    emit("polled");
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
