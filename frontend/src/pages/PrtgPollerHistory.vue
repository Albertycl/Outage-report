<template>
  <q-page class="app-container">
    <div class="page-head">
      <div>
        <h1 class="page-head__title">PRTG Alert History</h1>
        <div class="page-head__sub">Demo refresh history (no real PagerDuty call is made)</div>
      </div>
      <div class="page-head__actions">
        <q-btn
          no-caps
          unelevated
          color="primary"
          icon="refresh"
          label="Reload"
          :loading="isLoading"
          @click="fetchHistory"
        />
      </div>
    </div>

    <!-- Current state of the poller itself -->
    <div class="row q-col-gutter-sm q-mb-md">
      <div class="col-12 col-sm-6 col-md-3">
        <q-card flat bordered class="q-pa-sm">
          <div class="text-caption text-grey-7">Schedule</div>
          <div class="text-subtitle1 text-weight-medium">
            <q-icon
              :name="meta.scheduler_enabled ? 'schedule' : 'schedule_send'"
              :color="meta.scheduler_enabled ? 'green-7' : 'red-7'"
              size="xs"
            />
            {{
              meta.scheduler_enabled
                ? `every ${meta.poll_interval_minutes} min`
                : "background polling OFF"
            }}
          </div>
        </q-card>
      </div>

      <div class="col-12 col-sm-6 col-md-3">
        <q-card flat bordered class="q-pa-sm">
          <div class="text-caption text-grey-7">Right now</div>
          <div class="text-subtitle1 text-weight-medium">
            <template v-if="currentRun.running">
              <q-spinner-dots color="primary" size="sm" />
              running {{ currentRun.running_for_seconds }}s
              <span class="text-caption text-grey-7">
                ({{ currentRun.triggered_by }})
              </span>
            </template>
            <template v-else>
              <q-icon name="pause_circle_outline" color="grey-6" size="xs" />
              idle
            </template>
          </div>
        </q-card>
      </div>

      <div class="col-12 col-sm-6 col-md-3">
        <q-card flat bordered class="q-pa-sm">
          <div class="text-caption text-grey-7">Next run</div>
          <div class="text-subtitle1 text-weight-medium">
            <!-- null here means the job is not scheduled in this process, which
                 is what a paused or dead job looks like -->
            <q-icon
              :name="meta.next_run_at ? 'update' : 'report_problem'"
              :color="meta.next_run_at ? 'green-7' : 'orange-8'"
              size="xs"
            />
            {{ meta.next_run_at || "not scheduled" }}
          </div>
        </q-card>
      </div>

      <div class="col-12 col-sm-6 col-md-3">
        <q-card flat bordered class="q-pa-sm">
          <div class="text-caption text-grey-7">Success rate (shown runs)</div>
          <div class="text-subtitle1 text-weight-medium">
            <q-icon
              :name="successRate === 100 ? 'check_circle' : 'error_outline'"
              :color="successRateColor"
              size="xs"
            />
            {{ successRate }}% of {{ runs.length }}
          </div>
        </q-card>
      </div>
    </div>

    <!-- Filters -->
    <div class="row q-gutter-sm q-mb-md items-center">
      <q-select
        v-model="limit"
        :options="[25, 50, 100, 250, 500]"
        label="Runs to show"
        dense
        outlined
        emit-value
        map-options
        style="min-width: 140px"
        @update:model-value="fetchHistory"
      />
      <q-select
        v-model="infraFilter"
        :options="infraOptions"
        label="Infra"
        dense
        outlined
        emit-value
        map-options
        style="min-width: 140px"
        @update:model-value="fetchHistory"
      />
      <q-toggle v-model="failuresOnly" label="Failures only" color="negative" />
      <q-space />
      <div class="text-caption text-grey-7">
        History is kept for {{ meta.retention_days }} days
      </div>
    </div>

    <q-banner v-if="loadError" dense class="bg-red-1 text-red-10 q-mb-md" rounded>
      <template #avatar><q-icon name="cloud_off" color="red-7" /></template>
      Could not load history - {{ loadError }}
    </q-banner>

    <!-- The runs -->
    <q-table
      :rows="visibleRuns"
      :columns="columns"
      row-key="run_id"
      :loading="isLoading"
      :pagination="{ rowsPerPage: 25 }"
      flat
      bordered
      dense
      no-data-label="No poll runs recorded yet"
    >
      <template #body-cell-status="props">
        <q-td :props="props">
          <q-chip
            dense
            square
            :color="props.row.status === 'ok' ? 'green-2' : 'red-2'"
            :text-color="props.row.status === 'ok' ? 'green-10' : 'red-10'"
            :icon="props.row.status === 'ok' ? 'check_circle' : 'error'"
          >
            {{ props.row.status }}
          </q-chip>
        </q-td>
      </template>

      <template #body-cell-http_status_code="props">
        <q-td :props="props">
          <q-chip
            dense
            square
            :color="httpColor(props.row.http_status_code).bg"
            :text-color="httpColor(props.row.http_status_code).text"
          >
            {{ props.row.http_status_code }}
          </q-chip>
          <q-tooltip>{{ httpMeaning(props.row.http_status_code) }}</q-tooltip>
        </q-td>
      </template>

      <template #body-cell-triggered_by="props">
        <q-td :props="props">
          <q-icon
            :name="props.row.triggered_by === 'scheduler' ? 'schedule' : 'touch_app'"
            size="xs"
            class="q-mr-xs"
          />
          {{ props.row.triggered_by }}
        </q-td>
      </template>

      <!-- One line per infra inside the run -->
      <template #body-cell-infras="props">
        <q-td :props="props">
          <div
            v-for="infra in props.row.infras"
            :key="infra.infra_name + infra.run_id"
            class="q-mb-xs"
          >
            <q-icon
              :name="infra.status === 'ok' ? 'check_circle' : 'error'"
              :color="infra.status === 'ok' ? 'green-7' : 'red-7'"
              size="xs"
            />
            <span class="text-weight-medium q-ml-xs">
              {{ infra.infra_name.toUpperCase() }}
            </span>
            <span class="q-ml-xs">
              {{ infra.status === "ok" ? `${infra.alert_count} open` : infra.status }}
            </span>
            <span class="text-grey-7 q-ml-xs" v-if="infra.duration_seconds !== null">
              ({{ infra.duration_seconds }}s)
            </span>
            <div
              v-if="infra.error_message"
              class="text-caption text-red-9 q-ml-lg ellipsis"
              style="max-width: 620px"
            >
              {{ infra.error_message }}
              <q-tooltip class="text-body2" style="max-width: 600px">
                {{ infra.error_message }}
              </q-tooltip>
            </div>
          </div>
        </q-td>
      </template>
    </q-table>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import axios from "axios";

import { API_BASE_URL } from "src/config/api";
import { INFRA_NAMES } from "src/config/infra";

// Matches the poll interval so the page keeps pace with the poller without
// hammering the backend.
const RELOAD_EVERY_MS = 30 * 1000;

const runs = ref([]);
const meta = ref({});
const currentRun = ref({ running: false });
const isLoading = ref(false);
const loadError = ref(null);
const limit = ref(100);
const infraFilter = ref(null);
const failuresOnly = ref(false);
let timer = null;

const infraOptions = [
  { label: "All", value: null },
  ...INFRA_NAMES.map((name) => ({ label: name.toUpperCase(), value: name })),
];

const columns = [
  { name: "run_at", label: "When", field: "run_at", align: "left", sortable: true },
  { name: "status", label: "Result", field: "status", align: "left" },
  {
    name: "http_status_code",
    label: "HTTP",
    field: "http_status_code",
    align: "left",
    sortable: true,
  },
  {
    name: "triggered_by",
    label: "Trigger",
    field: "triggered_by",
    align: "left",
    sortable: true,
  },
  {
    name: "total_alerts",
    label: "Alerts",
    field: "total_alerts",
    align: "right",
    sortable: true,
  },
  { name: "infras", label: "Per infra", field: "infras", align: "left" },
];

const visibleRuns = computed(() =>
  failuresOnly.value ? runs.value.filter((r) => r.status !== "ok") : runs.value
);

const successRate = computed(() => {
  if (!runs.value.length) return 0;
  const ok = runs.value.filter((r) => r.status === "ok").length;
  return Math.round((ok / runs.value.length) * 100);
});

const successRateColor = computed(() => {
  if (successRate.value === 100) return "green-7";
  if (successRate.value >= 90) return "orange-8";
  return "red-7";
});

function httpColor(code) {
  if (code === 200) return { bg: "green-2", text: "green-10" };
  if (code === 207) return { bg: "orange-2", text: "orange-10" };
  return { bg: "red-2", text: "red-10" };
}

function httpMeaning(code) {
  return (
    {
      200: "200 - every configured infra polled successfully",
      207: "207 - partial: at least one infra polled, at least one failed",
      500: "500 - the run failed writing to the database, or no API token is set",
      503: "503 - no infra could be polled at all",
    }[code] || `${code}`
  );
}

async function fetchHistory() {
  isLoading.value = true;
  try {
    const params = { limit: limit.value };
    if (infraFilter.value) params.infra = infraFilter.value;

    const { data } = await axios.get(`${API_BASE_URL}/prtg_alerts_history`, {
      params,
    });
    runs.value = data.runs || [];
    currentRun.value = data.current_run || { running: false };
    meta.value = {
      scheduler_enabled: data.scheduler_enabled,
      poll_interval_minutes: data.poll_interval_minutes,
      retention_days: data.retention_days,
      next_run_at: data.next_run_at,
    };
    loadError.value = null;
  } catch (err) {
    loadError.value = err.message || "backend unreachable";
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchHistory();
  timer = setInterval(fetchHistory, RELOAD_EVERY_MS);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>
