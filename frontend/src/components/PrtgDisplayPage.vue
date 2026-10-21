<template>
  <div class="app-card metric-card column">
    <div class="app-card__head">
      <span class="app-card__title">{{ cardData.title }}</span>
      <span v-if="!isLoading && !error" class="app-card__badge">PRTG</span>
    </div>

    <div class="relative-position col metric-card__body">
      <q-inner-loading :showing="isLoading">
        <q-spinner-dots size="42px" color="primary" />
      </q-inner-loading>

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

      <!-- Two labelled figures rather than a stack of bare numbers: the old
           card showed the connection count and the down count in different
           type sizes with nothing saying which was which. -->
      <div v-else-if="!isLoading" class="row q-col-gutter-sm q-pa-md items-stretch">
        <div class="col-7">
          <!-- No reading is not the same fact as a reading of zero. The old
               card ran the value through `parseInt(...) || 0`, so an LTM the
               backend has never managed to query showed a confident "0" new
               connections - which reads as a dead LTM rather than as a dead
               query. It says so instead. -->
          <component
            :is="cardData.labelLink ? 'a' : 'div'"
            :href="cardData.labelLink"
            :target="cardData.labelLink ? '_blank' : undefined"
            rel="noopener noreferrer"
            class="tile"
            :class="cardData.hasReading ? '' : 'tile--unknown'"
          >
            <template v-if="cardData.hasReading">
              <div class="metric-value metric-value--sm">{{ cardData.mainValue }}</div>
              <div class="metric-label">
                New connections
                <template v-if="cardData.label && cardData.label !== 'n/a'">
                  ({{ cardData.label }})
                </template>
                <q-icon
                  v-if="cardData.labelLink"
                  name="open_in_new"
                  size="11px"
                  class="q-ml-xs"
                />
              </div>
              <q-tooltip v-if="cardData.labelLink">
                The LTM new-connection sensor in PRTG
              </q-tooltip>
            </template>

            <template v-else>
              <q-icon name="help_outline" size="26px" color="orange-8" />
              <div class="tile__unknown-value">No reading</div>
              <div class="metric-label">New connections</div>
              <q-tooltip>
                The backend has no new-connection value for this LTM: it has not
                been able to query the PRTG sensor. This is not a count of zero
                connections.
              </q-tooltip>
            </template>
          </component>
        </div>

        <div class="col-5">
          <component
            :is="cardData.secondaryValueLink ? 'a' : 'div'"
            :href="cardData.secondaryValueLink"
            :target="cardData.secondaryValueLink ? '_blank' : undefined"
            rel="noopener noreferrer"
            class="tile"
            :class="cardData.secondaryValue ? 'tile--alerting' : ''"
            title="View down sensors"
          >
            <div class="metric-value" :class="valueClass(cardData.secondaryValue)">
              {{ cardData.secondaryValue }}
            </div>
            <div class="metric-label">Down sensors</div>
          </component>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import axios from "axios";

import { API_BASE_URL } from "src/config/api";
import { prtgSensorLink } from "src/config/infra";
const props = defineProps({
  infraName: {
    type: String,
    required: true,
  },
});

// The PagerDuty poller and the LTM reader both write on their own schedule, so
// the card re-reads what they last wrote rather than waiting for someone to
// reload the page. Matches the JKB card; the banner above the cards is what
// says whether the pollers themselves are alive.
const REFRESH_EVERY_MS = 60 * 1000;

const isLoading = ref(true);
const error = ref(null);
const cardData = ref({});
let timer = null;

// A zero is the normal state and should recede; anything above it is the
// reason someone is looking at the dashboard.
function valueClass(count) {
  return Number(count) > 0 ? "metric-value--alert" : "metric-value--quiet";
}

async function fetchData({ silent = false } = {}) {
  // a background refresh must not blank the card it is refreshing
  isLoading.value = !silent;
  error.value = null;

  try {
    const response = await axios.get(
      `${API_BASE_URL}/sending_prtg_info_to_frontend_for_each_infra/${props.infraName}`
    );

    const apiDataArray = response.data.data;

    if (!apiDataArray || apiDataArray.length === 0) {
      throw new Error(`No data returned for ${props.infraName}`);
    }

    const apiData = apiDataArray[0];

    const sensorLink = prtgSensorLink(apiData.infra_name, apiData.sensor_id);

    const detailPageLink = `/prtg_detail/${props.infraName}`;

    // lastvalue is written by /ltm_new_connection_sensor_details. The PagerDuty
    // poller creates the row if that route has never run, leaving this unset,
    // so it must not be assumed to be a string.
    const lastValue = String(apiData.lastvalue ?? "n/a");

    // Only a value that actually parses is a reading. Anything else - unset,
    // "n/a", whatever else the row was created with - means the backend never
    // got an answer out of PRTG, and the card must not present that as a count.
    const parsed = parseInt(lastValue.replace(/,/g, ""), 10);
    const hasReading = Number.isFinite(parsed);

    cardData.value = {
      title: props.infraName.toUpperCase(),
      hasReading,
      mainValue: hasReading ? parsed.toLocaleString() : null,
      label: lastValue.split(" ")[1] || "n/a",
      labelLink: sensorLink,
      secondaryValue: apiData.down_count || 0,
      secondaryValueLink: detailPageLink,
    };
  } catch (err) {
    console.error(`Failed to fetch PRTG data for ${props.infraName}:`, err);
    error.value = "PRTG data unavailable";
    cardData.value = {
      title: props.infraName.toUpperCase(),
      hasReading: false,
    };
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchData();
  timer = setInterval(() => fetchData({ silent: true }), REFRESH_EVERY_MS);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>

<style scoped>
.metric-card {
  height: 100%;
  min-height: 190px;
}

.metric-card__body {
  min-height: 130px;
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

.tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 14px 10px;
  border: 1px solid var(--app-border);
  border-radius: 10px;
  background: var(--app-surface-muted);
  text-decoration: none;
  transition: border-color 0.18s ease, background-color 0.18s ease;
}

a.tile:hover {
  border-color: var(--app-primary);
  background: rgba(37, 99, 235, 0.05);
}

.tile--alerting {
  border-color: rgba(220, 38, 38, 0.35);
  background: #FEF2F2;
}

a.tile--alerting:hover {
  border-color: var(--app-negative);
  background: #FEE2E2;
}

/* "no reading" is a third state, neither quiet nor alerting: amber, so it is
   visibly not a number someone can act on. */
.tile--unknown {
  border-color: #FDE68A;
  background: #FFFBEB;
}

a.tile--unknown:hover {
  border-color: var(--app-warning);
  background: #FEF3C7;
}

.tile__unknown-value {
  margin-top: 4px;
  font-size: 17px;
  font-weight: 600;
  color: #92400E;
}

/* The connection count runs to six figures, so it cannot use the same size as
   a single-digit alert count without wrapping. */
.metric-value--sm {
  font-size: 30px;
  color: var(--app-ink);
}

.metric-label {
  text-align: center;
}

@media (max-width: 599px) {
  .metric-value {
    font-size: 32px;
  }
  .metric-value--sm {
    font-size: 24px;
  }
}
</style>
