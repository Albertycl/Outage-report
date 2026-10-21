<template>
  <div class="app-card metric-card column">
    <div class="app-card__head">
      <span class="app-card__title">{{ cardData.title }}</span>
      <span v-if="!isLoading && !error" class="app-card__badge">JKB</span>
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

      <div v-else-if="!isLoading" class="jkb-body q-pa-md">
        <component
          :is="cardData.mainValueLink ? 'a' : 'div'"
          :href="cardData.mainValueLink"
          :target="cardData.mainValueLink ? '_blank' : undefined"
          rel="noopener noreferrer"
          class="tile"
          :class="hasAlerts ? 'tile--alerting' : ''"
        >
          <!-- a non-zero alert count is the thing someone opened this page
               for, so it is red rather than the same grey as a quiet zero -->
          <div
            class="metric-value"
            :class="hasAlerts ? 'metric-value--alert' : 'metric-value--quiet'"
          >
            {{ cardData.mainValue }}
          </div>
          <div class="metric-label">
            Alerting
            <q-icon v-if="cardData.mainValueLink" name="open_in_new" size="11px"
              class="q-ml-xs" />
          </div>
          <q-tooltip v-if="cardData.mainValueLink">
            Every alerting JKB sensor in this infra
          </q-tooltip>
        </component>

        <!-- Which items are down. The count alone meant opening the detail page
             to answer the first question anyone asks of it. -->
        <div class="col alert-list">
          <template v-if="alerts.length">
            <a
              v-for="alert in alerts"
              :key="alert.id"
              :href="alert.link_for_snapshot || undefined"
              :target="alert.link_for_snapshot ? '_blank' : undefined"
              rel="noopener noreferrer"
              class="alert-row"
            >
              <q-icon name="error" color="negative" size="14px" class="alert-row__icon" />
              <span class="alert-row__text">
                <span class="alert-row__name">{{ alert.task_name }}</span>
                <span class="alert-row__meta">
                  {{ [alert.group_name, alert.task_summary].filter(Boolean).join(" · ") }}
                </span>
              </span>
              <q-icon
                v-if="alert.link_for_snapshot"
                name="open_in_new"
                size="12px"
                class="alert-row__go"
              />
              <q-tooltip v-if="alert.link_for_snapshot">
                Open the snapshot for this monitor item
              </q-tooltip>
            </a>
          </template>

          <div v-else class="alert-list__empty">
            <q-icon name="check_circle" color="positive" size="16px" class="q-mr-xs" />
            Nothing alerting
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import axios from "axios";

import { API_BASE_URL } from "src/config/api";
const props = defineProps({
  infraName: {
    type: String,
    required: true,
  },
});

// The backend runs the JKB pipeline on a schedule, so the card re-reads what
// that pipeline last wrote rather than waiting for someone to reload the page.
// The banner above the cards is what says whether the pipeline itself is alive.
const REFRESH_EVERY_MS = 60 * 1000;

const isLoading = ref(true);
const error = ref(null);
const cardData = ref({});
const alerts = ref([]);
let timer = null;

const hasAlerts = computed(() => Number(cardData.value.mainValue) > 0);

async function fetchData({ silent = false } = {}) {
  // a background refresh must not blank the card it is refreshing
  isLoading.value = !silent;
  error.value = null;
  try {
    const response = await axios.get(
      `${API_BASE_URL}/sending_jkb_info_to_frontend_for_each_infra/${props.infraName}`
    );

    const apiDataArray = response.data.data;

    if (!apiDataArray || apiDataArray.length === 0) {
      throw new Error(`No data returned for ${props.infraName}`);
    }

    const apiData = apiDataArray[0];

    // UPDATED: Dynamically generate the link for the main value (alert count)
    const jkbDetailLink = `/jkb_detail/${props.infraName}`;

    // UPDATED: Mapping the new API fields and the generated link to the card's data structure.
    cardData.value = {
      title: props.infraName.toUpperCase(),
      mainValue: apiData.alert_count,
      mainValueLink: jkbDetailLink, // Storing the generated link
      label: "Alerts",
      labelLink: null,
      secondaryValueLink: null,
    };
  } catch (err) {
    console.error(`Failed to fetch JKB data for ${props.infraName}:`, err);
    error.value = "JKB data unavailable";
    cardData.value = { title: props.infraName.toUpperCase() };
  } finally {
    isLoading.value = false;
  }

  // The list beside the count. It is fetched separately and never fails the
  // card: the count is still worth showing if only the detail call breaks.
  try {
    const { data } = await axios.get(
      `${API_BASE_URL}/get_jkb_alert_details/${props.infraName}`
    );
    alerts.value = Array.isArray(data) ? data : [];
  } catch (err) {
    console.error(`Failed to fetch JKB alert details for ${props.infraName}:`, err);
    alerts.value = [];
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

/* Plain flex with a gap rather than Quasar's q-gutter, whose negative margins
   pushed this row a few pixels past the card and got it clipped at phone
   width by the section's overflow:hidden. */
.jkb-body {
  display: flex;
  align-items: stretch;
  gap: 12px;
  min-width: 0;
}

.tile {
  /* the count is a fixed-width anchor; the list beside it takes the rest */
  flex: none;
  width: 132px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 104px;
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

.metric-label {
  text-align: center;
}

/* The alerting items. Capped in height so one bad night cannot push the JKB
   section down the page; the rest scrolls. */
.alert-list {
  min-width: 0;
  max-height: 132px;
  overflow-y: auto;
}

.alert-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
}

.alert-row:hover {
  background: var(--app-surface-muted);
}

.alert-row__icon {
  margin-top: 2px;
  flex: none;
}

.alert-row__text {
  min-width: 0;
  flex: 1;
}

.alert-row__name {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--app-ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.alert-row__meta {
  display: block;
  font-size: 11px;
  color: var(--app-ink-subtle);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.alert-row__go {
  flex: none;
  margin-top: 3px;
  color: var(--app-ink-subtle);
}

.alert-list__empty {
  display: flex;
  align-items: center;
  height: 100%;
  padding-left: 8px;
  font-size: 13px;
  color: var(--app-ink-subtle);
}

@media (max-width: 599px) {
  .metric-value {
    font-size: 32px;
  }

  /* On a phone there is no room for a 132px counter and a readable item name
     side by side - the names ellipsised to nothing. They stack instead. */
  .jkb-body {
    flex-direction: column;
  }

  .tile {
    width: 100%;
    min-height: 88px;
  }

  .alert-list {
    max-height: 168px;
  }

  .alert-list__empty {
    height: auto;
    padding: 8px;
  }
}
</style>
