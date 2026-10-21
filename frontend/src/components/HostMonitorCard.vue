<template>
  <div class="app-card metric-card column">
    <!-- Header. The infra name labels the numbers below it, so it is a small
         upper-case label rather than the display-size heading it was: the
         counts are what the card is for. -->
    <div class="app-card__head">
      <span class="app-card__title">{{ title }}</span>
      <span v-if="!isLoading && !error" class="app-card__badge">HostMonitor</span>
    </div>

    <div class="relative-position col metric-card__body">
      <q-inner-loading :showing="isLoading">
        <q-spinner-dots size="42px" color="primary" />
      </q-inner-loading>

      <!-- Error State -->
      <div v-if="error" class="column items-center justify-center full-height q-pa-lg">
        <q-icon name="cloud_off" color="negative" size="32px" />
        <div class="text-body2 text-negative q-mt-sm">{{ error }}</div>
        <q-btn
          no-caps
          outline
          size="sm"
          color="primary"
          label="Retry"
          class="q-mt-md"
          @click="fetchData"
        />
      </div>

      <!-- Data Display -->
      <div v-else-if="!isLoading" class="row full-height">
        <template v-for="(col, index) in columns" :key="col.header">
          <div class="col column q-pa-md">
            <!-- Column Header. With a single HostMonitor there is nothing
                 to tell apart, so the name is just noise above the numbers;
                 it comes back if a second one is ever added. -->
            <div v-if="columns.length > 1" class="metric-card__colname">
              {{ col.header }}
            </div>

            <!-- Values Section. Two boxes rather than two bare numbers: side
                 by side and unlabelled, "1" and "1" read as a single "11".
                 Each one opens the report page filtered to its own side of
                 the split, which is the list of what is actually in it. -->
            <div class="row items-stretch q-col-gutter-sm col items-center">
              <div v-if="col.numericHeader === 82" class="col">
                <router-link
                  :to="reportLink(true)"
                  class="count-box"
                  :class="col.ltmValue ? 'count-box--alerting' : ''"
                >
                  <div class="metric-value" :class="valueClass(col.ltmValue)">
                    {{ col.ltmValue }}
                  </div>
                  <div class="metric-label">LTM</div>
                  <q-tooltip>
                    Alerting sensors on the LTM (a pool or virtual server).
                    Click to list every LTM sensor in this infra.
                  </q-tooltip>
                </router-link>
              </div>

              <div class="col">
                <router-link
                  :to="reportLink(false)"
                  class="count-box"
                  :class="col.notValue ? 'count-box--alerting' : ''"
                >
                  <div class="metric-value" :class="valueClass(col.notValue)">
                    {{ col.notValue }}
                  </div>
                  <div class="metric-label">
                    {{ col.numericHeader === 82 ? "Not LTM" : "Alerting" }}
                  </div>
                  <q-tooltip>
                    Alerting sensors that are not on the LTM. Click to list
                    every non-LTM sensor in this infra.
                  </q-tooltip>
                </router-link>
              </div>
            </div>

            <!-- Total sensors. The number on its own reads as another alert
                 count next to LTM / NOT, so it says what it is. -->
            <a
              :href="`/host_monitor_detail_page/${props.infraName}/${col.ip}/`"
              target="_blank"
              rel="noopener noreferrer"
              class="metric-card__total"
            >
              <span class="metric-card__total-label">Total sensors</span>
              <span class="metric-card__total-value tabular-nums">{{ col.footer }}</span>
              <q-tooltip>
                Every test in this infra's HostMonitor report, alerting or not.
                Click for the alert detail page.
              </q-tooltip>
            </a>
          </div>

          <q-separator vertical v-if="index < columns.length - 1" />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

import { API_BASE_URL } from "src/config/api";
const props = defineProps({
  infraName: {
    type: String,
    required: true,
  },
});

// Deep link into the report page, already filtered to one side of the split.
function reportLink(inLtm) {
  return {
    path: "/hostmonitor_report",
    query: { infra: props.infraName, in_ltm: String(inLtm) },
  };
}

// A zero is the normal state and should recede; anything above it is the
// reason someone is looking at the dashboard.
function valueClass(count) {
  return count ? "metric-value--alert" : "metric-value--quiet";
}

const isLoading = ref(true);
const error = ref(null);
const title = ref("");
const columns = ref([]);

async function fetchData() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await axios.get(
      `${API_BASE_URL}/sending_hostmonitor_to_frontend_for_each_infra/${props.infraName}`
    );
    const apiData = response.data.data;

    const desiredOrder = [94, 93, 82];
    apiData.sort((a, b) => {
      const headerA = parseInt(a.hostmonitor_ip.split(".").pop(), 10);
      const headerB = parseInt(b.hostmonitor_ip.split(".").pop(), 10);
      return desiredOrder.indexOf(headerA) - desiredOrder.indexOf(headerB);
    });

    const headerNameMap = {
      94: "EXT_ISP_94",
      93: "EXT_ISP_93",
      82: "INT_82",
    };

    const formattedColumns = apiData.map((item) => {
      const numericHeader = parseInt(item.hostmonitor_ip.split(".").pop(), 10);
      return {
        numericHeader: numericHeader,
        header: headerNameMap[numericHeader] || numericHeader,
        ltmValue: parseInt(item.number_of_alerts_in_ltm, 10),
        notValue: parseInt(item.number_of_alerts_not_in_ltm, 10),
        footer: parseInt(item.total_sensor_for_this_infra, 10),
        ip: item.hostmonitor_ip,
      };
    });

    columns.value = formattedColumns;
    title.value = props.infraName.toUpperCase();
  } catch (err) {
    console.error(`Failed to fetch data for ${props.infraName}:`, err);
    error.value = "Could not load data.";
    title.value = props.infraName.toUpperCase();
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
/* Every card in a row is the same height so the totals line up across infras. */
.metric-card {
  height: 100%;
  min-height: 260px;
}

.metric-card__body {
  min-height: 180px;
}

.app-card__badge {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--app-ink-subtle);
  background: var(--app-surface-muted);
  border: 1px solid var(--app-border);
  border-radius: 999px;
  padding: 2px 8px;
}

.metric-card__colname {
  margin-bottom: 10px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--app-ink-subtle);
  text-align: center;
}

/* The LTM / NOT LTM counters. Boxed and spaced so two single digits cannot
   read as one two-digit number. */
.count-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 14px 10px;
  border: 1px solid var(--app-border);
  border-radius: 10px;
  background: var(--app-surface-muted);
  text-decoration: none;
  transition: border-color 0.18s ease, background-color 0.18s ease;
}

.count-box:hover {
  border-color: var(--app-primary);
  background: rgba(37, 99, 235, 0.05);
}

/* a non-zero count is the thing worth noticing on the dashboard */
.count-box--alerting {
  border-color: rgba(220, 38, 38, 0.35);
  background: #FEF2F2;
}

.count-box--alerting:hover {
  border-color: var(--app-negative);
  background: #FEE2E2;
}

/* The total is context for the counts above, so it sits on one quiet line
   instead of forming a third stacked figure. */
.metric-card__total {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
  margin-top: 14px;
  padding-top: 10px;
  border-top: 1px dashed var(--app-border);
  text-decoration: none;
}

.metric-card__total-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--app-ink-subtle);
}

.metric-card__total-value {
  font-size: 17px;
  font-weight: 600;
  color: var(--app-ink-muted);
}

.metric-card__total:hover .metric-card__total-value {
  color: var(--app-primary);
}

@media (max-width: 599px) {
  .metric-value {
    font-size: 34px;
  }
}
</style>
