<template>
  <q-page class="app-container">
    <!-- Page head. Matches the dashboard's: title and subtitle on the left,
         the actions for this page on the right. Where you are is stated by the
         header nav, so the page does not repeat it as a back button. -->
    <div class="page-head">
      <div>
        <h1 class="page-head__title">HostMonitor Reports</h1>
        <div class="page-head__sub">
          Every read of the report files
        </div>
      </div>
      <div class="page-head__actions">
        <q-btn
          no-caps
          outline
          color="grey-8"
          icon="play_arrow"
          label="Read now"
          :loading="isReading"
          @click="readNow"
        />
        <q-btn
          no-caps
          unelevated
          color="primary"
          icon="refresh"
          label="Reload"
          :loading="isLoading"
          @click="loadEverything"
        />
      </div>
    </div>

    <q-banner
      v-if="health.problems && health.problems.length"
      dense
      rounded
      class="bg-red-1 text-red-10 q-mb-md"
    >
      <template #avatar><q-icon name="report_problem" color="red-7" /></template>
      <div v-for="problem in health.problems" :key="problem">{{ problem }}</div>
    </q-banner>

    <q-banner v-if="loadError" dense rounded class="bg-red-1 text-red-10 q-mb-md">
      <template #avatar><q-icon name="cloud_off" color="red-7" /></template>
      Could not load the reports - {{ loadError }}
    </q-banner>

    <!-- State of the reader itself -->
    <div class="row q-col-gutter-sm q-mb-md">
      <div class="col-12 col-sm-6 col-md-3">
        <q-card flat bordered class="q-pa-sm full-height">
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
                : "scheduled reading OFF"
            }}
          </div>
          <!-- null here means the job is not scheduled in this process, which
               is what a paused or dead job looks like -->
          <div class="text-caption text-grey-7">
            next: {{ meta.next_run_at || "not scheduled" }}
          </div>
        </q-card>
      </div>

      <div class="col-12 col-sm-6 col-md-3">
        <q-card flat bordered class="q-pa-sm full-height">
          <div class="text-caption text-grey-7">Last read</div>
          <div class="text-subtitle1 text-weight-medium">
            {{ latest.run_at || "never" }}
          </div>
          <div class="text-caption" :class="ageClass">
            <template v-if="latest.age_minutes !== null && latest.age_minutes !== undefined">
              {{ latest.age_minutes }} min ago ({{ latest.triggered_by }})
            </template>
            <template v-else>the reports have not been read yet</template>
          </div>
        </q-card>
      </div>

      <div class="col-6 col-md-3">
        <q-card flat bordered class="q-pa-sm text-center full-height">
          <div class="text-h5 text-weight-bold text-grey-8">
            {{ latest.total_tests ?? "-" }}
          </div>
          <div class="text-caption text-grey-7">tests across the reports</div>
        </q-card>
      </div>

      <div class="col-6 col-md-3">
        <q-card flat bordered class="q-pa-sm text-center full-height">
          <!-- The same split the dashboard card shows: a test named after a
               load balancer object (Po.../VS...) is on the LTM. -->
          <div class="row justify-center no-wrap" style="gap: 28px">
            <div>
              <div
                class="text-h5 text-weight-bold"
                :class="latest.ltm_alert_count ? 'text-red-8' : 'text-green-8'"
              >
                {{ latest.ltm_alert_count ?? "-" }}
              </div>
              <div class="text-overline text-grey-6">LTM</div>
            </div>
            <div>
              <div
                class="text-h5 text-weight-bold"
                :class="latest.not_ltm_alert_count ? 'text-red-8' : 'text-green-8'"
              >
                {{ latest.not_ltm_alert_count ?? "-" }}
              </div>
              <div class="text-overline text-grey-6">NOT</div>
            </div>
          </div>
          <div class="text-caption text-grey-7">alerting</div>
        </q-card>
      </div>
    </div>

    <!-- One card per infra: each has its own report file, and one of them
         failing to read says nothing about the other. -->
    <div class="row q-col-gutter-sm q-mb-md">
      <div
        v-for="infra in latest.infras || []"
        :key="infra.infra_name"
        class="col-12 col-md-6"
      >
        <q-card flat bordered class="q-pa-sm">
          <div class="row items-center q-gutter-sm">
            <div class="text-subtitle1 text-weight-bold text-grey-8">
              {{ infra.infra_name.toUpperCase() }}
            </div>
            <q-badge
              :color="runStatusColor(infra.status)"
              :label="infra.status"
            />
            <q-space />
            <div class="text-caption text-grey-7">
              {{ infra.total_tests }} tests
            </div>
            <div
              class="text-caption text-weight-medium"
              :class="infra.alert_count ? 'text-red-8' : 'text-green-8'"
            >
              {{ infra.alert_count }} alerting
            </div>
          </div>

          <div class="row q-gutter-md q-mt-xs text-caption text-grey-8">
            <div>
              LTM
              <b :class="infra.ltm_alert_count ? 'text-red-8' : 'text-green-8'">
                {{ infra.ltm_alert_count }}
              </b>
              <span class="text-grey-6">of {{ infra.ltm_test_count }}</span>
            </div>
            <div>
              not LTM
              <b :class="infra.not_ltm_alert_count ? 'text-red-8' : 'text-green-8'">
                {{ infra.not_ltm_alert_count }}
              </b>
              <span class="text-grey-6">of {{ infra.not_ltm_test_count }}</span>
            </div>
          </div>

          <div class="row q-gutter-md q-mt-xs text-caption text-grey-8">
            <div>Bad <b class="text-red-8">{{ infra.bad_count }}</b></div>
            <div>Unknown <b class="text-orange-9">{{ infra.unknown_count }}</b></div>
            <div>Good <b class="text-green-8">{{ infra.good_count }}</b></div>
            <q-space />
            <!-- HostMonitor's own stamp. A file we keep reading successfully
                 but that HostMonitor stopped rewriting is stale in a way the
                 read time alone cannot show. -->
            <div>generated {{ infra.report_generated_at || "-" }}</div>
          </div>

          <div
            v-if="infra.error_message"
            class="text-caption text-red-9 q-mt-xs ellipsis"
          >
            {{ infra.error_message }}
            <q-tooltip class="text-body2" style="max-width: 600px">
              {{ infra.error_message }}
            </q-tooltip>
          </div>
        </q-card>
      </div>
    </div>

    <!-- The tests -->
    <div class="row items-center q-gutter-sm q-mb-sm">
      <div class="text-subtitle1 text-weight-medium text-grey-8">Tests</div>
      <q-select
        v-model="infraFilter"
        :options="infraOptions"
        label="Infra"
        dense
        outlined
        emit-value
        map-options
        style="min-width: 140px"
        @update:model-value="loadEverything"
      />
      <q-select
        v-model="ltmFilter"
        :options="ltmOptions"
        label="LTM"
        dense
        outlined
        emit-value
        map-options
        style="min-width: 150px"
      />
      <q-toggle v-model="alertsOnly" label="Alerting only" color="negative" />
    </div>

    <q-table
      :rows="visibleTests"
      :columns="testColumns"
      row-key="id"
      :loading="isLoading"
      :pagination="{ rowsPerPage: 25 }"
      flat
      bordered
      dense
      no-data-label="No tests in the last reading"
    >
      <template #body-cell-infra_name="props">
        <q-td :props="props">
          <q-badge outline color="grey-8" :label="props.row.infra_name" />
        </q-td>
      </template>

      <template #body-cell-in_ltm="props">
        <q-td :props="props">
          <q-badge
            :color="props.row.in_ltm ? 'indigo-6' : 'grey-6'"
            :label="props.row.in_ltm ? 'LTM' : 'not LTM'"
          />
        </q-td>
      </template>

      <template #body-cell-status_class="props">
        <q-td :props="props">
          <q-badge
            :color="statusColor(props.row.status_class)"
            :label="props.row.status_class"
          />
          <span v-if="props.row.status_text" class="q-ml-sm text-grey-8">
            {{ props.row.status_text }}
          </span>
        </q-td>
      </template>

      <template #body-cell-recurrences="props">
        <q-td :props="props">
          <!-- HostMonitor counts consecutive results in the same state, so a
               large number on a Bad test is how long it has been down. -->
          <span :class="props.row.is_alert ? 'text-red-9 text-weight-medium' : ''">
            {{ props.row.recurrences ?? "-" }}
          </span>
        </q-td>
      </template>
    </q-table>

    <!-- The readings behind this one -->
    <div class="row items-center q-gutter-sm q-mt-lg q-mb-sm">
      <div class="text-subtitle1 text-weight-medium text-grey-8">
        Recent readings
      </div>
      <q-toggle v-model="failuresOnly" label="Failures only" color="negative" />
      <q-space />
      <div class="text-caption text-grey-7">
        Kept for {{ meta.retention_days }} days
      </div>
    </div>

    <q-table
      :rows="visibleRuns"
      :columns="runColumns"
      row-key="run_id"
      :loading="isLoading"
      :pagination="{ rowsPerPage: 15 }"
      flat
      bordered
      dense
      no-data-label="The reports have not been read yet"
    >
      <template #body-cell-status="props">
        <q-td :props="props">
          <q-badge
            :color="runStatusColor(props.row.status)"
            :label="props.row.status"
          />
        </q-td>
      </template>

      <template #body-cell-infras="props">
        <q-td :props="props">
          <div
            v-for="infra in props.row.infras"
            :key="infra.infra_name"
            class="row items-center q-gutter-xs"
          >
            <q-badge
              :color="runStatusColor(infra.status)"
              :label="infra.infra_name"
            />
            <span class="text-caption text-grey-8">
              {{ infra.alert_count }}/{{ infra.total_tests }} alerting
            </span>
            <span
              v-if="infra.error_message"
              class="text-caption text-red-9 ellipsis"
              style="max-width: 420px"
            >
              {{ infra.error_message }}
              <q-tooltip class="text-body2" style="max-width: 600px">
                {{ infra.error_message }}
              </q-tooltip>
            </span>
          </div>
        </q-td>
      </template>
    </q-table>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import axios from "axios";

import { API_BASE_URL } from "src/config/api";

// The backend reads the files once a minute; this keeps the page in step with
// it without asking more often than there is anything new to see.
const RELOAD_EVERY_MS = 60 * 1000;

const route = useRoute();

const latest = ref({});
const tests = ref([]);
const runs = ref([]);
const meta = ref({});
const health = ref({});
const infraFilter = ref(null);
const alertsOnly = ref(false);
// null = both sides of the split, true = LTM only, false = everything else
const ltmFilter = ref(null);
const failuresOnly = ref(false);
const isLoading = ref(false);
const isReading = ref(false);
const loadError = ref(null);
let timer = null;

// Which button classes mean something is actually wrong. Mirrors
// REPORT_STATUS_CLASSES in the backend; the backend is what decides is_alert,
// this is only about colour.
const ALERT_CLASSES = ["Bad", "BadAck", "Unknown", "UnknAck"];

const infraOptions = computed(() => [
  { label: "All", value: null },
  ...(meta.value.infra_names || []).map((name) => ({
    label: name.toUpperCase(),
    value: name,
  })),
]);

const ltmOptions = [
  { label: "All", value: null },
  { label: "LTM only", value: true },
  { label: "Not LTM", value: false },
];

const testColumns = [
  { name: "infra_name", label: "Infra", field: "infra_name", align: "left", sortable: true },
  { name: "in_ltm", label: "LTM", field: "in_ltm", align: "left", sortable: true },
  { name: "folder_name", label: "Folder", field: "folder_name", align: "left", sortable: true },
  { name: "test_name", label: "Test", field: "test_name", align: "left", sortable: true },
  { name: "status_class", label: "Status", field: "status_class", align: "left", sortable: true },
  { name: "recurrences", label: "Recurrences", field: "recurrences", align: "right", sortable: true },
  { name: "reply", label: "Reply", field: "reply", align: "left" },
];

const runColumns = [
  { name: "run_at", label: "Read at", field: "run_at", align: "left", sortable: true },
  { name: "status", label: "Result", field: "status", align: "left" },
  { name: "triggered_by", label: "Trigger", field: "triggered_by", align: "left", sortable: true },
  { name: "total_tests", label: "Tests", field: "total_tests", align: "right", sortable: true },
  { name: "alert_count", label: "Alerting", field: "alert_count", align: "right", sortable: true },
  { name: "infras", label: "Per infra", field: "infras", align: "left" },
];

const visibleTests = computed(() =>
  tests.value.filter(
    (test) =>
      (!alertsOnly.value || test.is_alert) &&
      (ltmFilter.value === null || test.in_ltm === ltmFilter.value)
  )
);

const visibleRuns = computed(() =>
  failuresOnly.value
    ? runs.value.filter((run) => run.status !== "ok")
    : runs.value
);

const ageClass = computed(() => {
  const max = meta.value.max_data_age_minutes;
  const age = latest.value.age_minutes;
  if (age === null || age === undefined || !max) return "text-grey-7";
  return age > max ? "text-red-9 text-weight-medium" : "text-grey-7";
});

function statusColor(statusClass) {
  if (statusClass === "Good") return "green-7";
  if (ALERT_CLASSES.includes(statusClass)) {
    return statusClass.endsWith("Ack") ? "orange-8" : "red-7";
  }
  // Disabled / NotTested / OutOfSchedule / WaitForMaster: the test is not
  // currently saying anything about its target
  return "grey-6";
}

function runStatusColor(status) {
  return (
    {
      ok: "green-7",
      partial: "orange-8",
      error: "red-7",
      not_configured: "blue-7",
    }[status] || "grey-6"
  );
}

async function loadEverything() {
  isLoading.value = true;
  try {
    const params = infraFilter.value ? { infra: infraFilter.value } : {};

    const [latestResponse, historyResponse, healthResponse] = await Promise.all([
      axios.get(`${API_BASE_URL}/hostmonitor_report_latest`, { params }),
      axios.get(`${API_BASE_URL}/hostmonitor_report_history`, {
        params: { ...params, limit: 100 },
      }),
      // an unhealthy reader answers 503, which is the state we most want to
      // show, so it must not be treated as a failed request
      axios
        .get(`${API_BASE_URL}/health/hostmonitor_report`, {
          validateStatus: (status) => status === 200 || status === 503,
        })
        .catch(() => ({ data: {} })),
    ]);

    latest.value = latestResponse.data;
    tests.value = latestResponse.data.tests || [];
    meta.value = latestResponse.data;
    runs.value = historyResponse.data.runs || [];
    health.value = healthResponse.data || {};
    loadError.value = null;
  } catch (err) {
    loadError.value = err.message || "backend unreachable";
  } finally {
    isLoading.value = false;
  }
}

async function readNow() {
  isReading.value = true;
  try {
    await axios.get(`${API_BASE_URL}/refresh_hostmonitor_report`, {
      // a failed read is recorded and shown like any other; only a request
      // that never arrived is a page-level error
      validateStatus: () => true,
    });
    await loadEverything();
  } finally {
    isReading.value = false;
  }
}

onMounted(() => {
  // The dashboard card links straight to one side of the split, e.g.
  // /hostmonitor_report?infra=delta&in_ltm=true, so arrive with those filters
  // already applied rather than making the reader set them again.
  if (route.query.infra) infraFilter.value = String(route.query.infra);
  if (route.query.in_ltm !== undefined) {
    ltmFilter.value = String(route.query.in_ltm) === "true";
  }
  if (route.query.alerts_only !== undefined) {
    alertsOnly.value = String(route.query.alerts_only) === "true";
  }

  loadEverything();
  timer = setInterval(loadEverything, RELOAD_EVERY_MS);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>
