<template>
  <q-page class="app-container">
    <!-- Page toolbar. The refresh sequence used to blank the whole dashboard
         behind a full-screen spinner on every load; the cards fetch their own
         data anyway, so it is a progress bar here instead and the numbers stay
         readable while the sources are re-pulled. -->
    <div class="page-head">
      <div>
        <h1 class="page-head__title">Operations Dashboard</h1>
        <div class="page-head__sub">
          Alert status across HostMonitor, PRTG and JKB
          <span v-if="lastRefreshed"> &middot; refreshed {{ lastRefreshed }}</span>
        </div>
      </div>

      <div class="page-head__actions">
        <q-btn
          no-caps
          outline
          color="grey-8"
          icon="description"
          :label="$q.screen.xs ? 'Templates' : 'Incident Templates'"
          :dense="$q.screen.xs"
          @click="openTemplatesDialog"
        />
        <q-btn
          no-caps
          unelevated
          color="primary"
          icon="refresh"
          :label="$q.screen.xs ? 'Refresh' : 'Refresh All Data'"
          :loading="isRefreshing"
          :dense="$q.screen.xs"
          @click="triggerAllApis"
        />
      </div>
    </div>

    <q-linear-progress
      v-if="isRefreshing"
      indeterminate
      color="primary"
      size="2px"
      class="q-mb-md"
    />

    <!-- HostMonitor -->
    <section class="app-section app-section--hostmonitor">
      <div class="app-section__head">
        <div class="app-section__accent" />
        <div>
          <div class="app-section__title">HostMonitor</div>
          <div class="app-section__subtitle">
            Alerting tests per infra, split by LTM membership
          </div>
        </div>
        <q-space />
        <!-- Demo: every card shows seeded, made-up numbers. -->
        <q-btn
          no-caps
          flat
          dense
          color="primary"
          icon="article"
          label="Reports"
          to="/hostmonitor_report"
        >
          <q-tooltip>The HostMonitor reports for each infra, as they are read</q-tooltip>
        </q-btn>
      </div>

      <div class="app-section__body">
        <!-- Are the reports still being read? The cards below show whatever the
             last successful read wrote, so a failed read looks exactly like a
             quiet night. -->
        <HostMonitorReportStatus />
        <div class="row q-col-gutter-md">
          <div v-for="name in infraNames" :key="name" class="col-12 col-md-6">
            <HostMonitorCard :infra-name="name" />
          </div>
        </div>
      </div>
    </section>

    <!-- PRTG -->
    <section class="app-section app-section--prtg">
      <div class="app-section__head">
        <div class="app-section__accent" />
        <div>
          <div class="app-section__title">PRTG</div>
          <div class="app-section__subtitle">
            LTM new connections and down sensors, (demo data)
          </div>
        </div>
        <q-space />
        <q-btn
          no-caps
          flat
          dense
          color="primary"
          icon="history"
          label="History"
          to="/prtg_poller_history"
        >
          <q-tooltip>Every demo refresh</q-tooltip>
        </q-btn>
      </div>

      <div class="app-section__body">
        <!-- Is the PagerDuty poller alive? The cards below show whatever it
             last wrote, so a dead poller looks exactly like a quiet night. -->
        <PagerDutyPollerStatus />
        <div class="row q-col-gutter-md">
          <div v-for="name in infraNames" :key="name" class="col-12 col-md-6">
            <PrtgDisplayPage :infra-name="name" />
          </div>
        </div>
      </div>
    </section>

    <!-- JKB -->
    <section class="app-section app-section--jkb">
      <div class="app-section__head">
        <div class="app-section__accent" />
        <div>
          <div class="app-section__title">JKB</div>
          <div class="app-section__subtitle">Classified sensor alerts per infra</div>
        </div>
        <q-space />
        <q-btn
          no-caps
          flat
          dense
          color="primary"
          icon="history"
          label="History"
          to="/jkb_poll_history"
        >
          <q-tooltip>Every JKB run, each step's status and any errors</q-tooltip>
        </q-btn>
      </div>

      <div class="app-section__body">
        <!-- Is the JKB pipeline alive? The cards below show whatever it last
             wrote, so a dead pipeline looks exactly like a quiet night. -->
        <JkbPollerStatus @polled="reloadJkbCards" />
        <div class="row q-col-gutter-md">
          <div
            v-for="name in infraNames_for_jkb"
            :key="`${name}-${jkbCardsKey}`"
            class="col-12 col-md-6"
          >
            <JkbDisplayPage :infra-name="name" />
          </div>
        </div>
      </div>
    </section>

    <!-- Templates Dialog -->
    <q-dialog v-model="showTemplatesDialog">
      <q-card
        class="templates-dialog"
        :style="$q.screen.xs ? 'width: 95vw' : 'width: 1100px; max-width: 96vw'"
      >
        <q-card-section class="row items-center q-pb-sm">
          <div>
            <div class="text-subtitle1 text-weight-medium">Incident Report Templates</div>
            <div class="text-caption text-grey-7">
              Copy the wording for the stage the incident is at
            </div>
          </div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-separator />

        <q-inner-loading :showing="isFetchingTemplates">
          <q-spinner-dots size="42px" color="primary" />
        </q-inner-loading>

        <q-card-section v-if="!isFetchingTemplates" class="q-pt-none">
          <q-tabs
            v-model="tab"
            dense
            no-caps
            class="text-grey-7"
            active-color="primary"
            indicator-color="primary"
            align="left"
            narrow-indicator
          >
            <q-tab name="initial_update" label="Initial Update" />
            <q-tab name="action_update" label="Action Update" />
            <q-tab name="resolution" label="Resolution" />
          </q-tabs>

          <q-separator />

          <q-tab-panels v-model="tab" animated>
            <q-tab-panel v-for="key in templateKeys" :key="key" :name="key">
              <div class="row justify-end">
                <q-btn
                  no-caps
                  flat
                  dense
                  label="Copy"
                  icon="content_copy"
                  color="primary"
                  @click="copyTemplate(templates[key])"
                />
              </div>
              <pre class="template-body">{{ templates[key] }}</pre>
            </q-tab-panel>
          </q-tab-panels>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useQuasar, copyToClipboard } from "quasar";

// Component Imports
import HostMonitorCard from "src/components/HostMonitorCard.vue";
import HostMonitorReportStatus from "src/components/HostMonitorReportStatus.vue";
import PrtgDisplayPage from "src/components/PrtgDisplayPage.vue";
import JkbDisplayPage from "src/components/JkbDisplayPage.vue";
import PagerDutyPollerStatus from "src/components/PagerDutyPollerStatus.vue";
import JkbPollerStatus from "src/components/JkbPollerStatus.vue";

import { API_BASE_URL } from "src/config/api";
import { INFRA_NAMES, JKB_INFRA_NAMES } from "src/config/infra";
const $q = useQuasar();

// Reactive state variables
const isRefreshing = ref(false);
const lastRefreshed = ref("");

const infraNames = ref(INFRA_NAMES);
const infraNames_for_jkb = ref(JKB_INFRA_NAMES);

// Bumped after a manual JKB run so the cards remount and re-read their own
// endpoint; they poll on their own too, this just skips the wait.
const jkbCardsKey = ref(0);
function reloadJkbCards() {
  jkbCardsKey.value += 1;
}

// Templates Dialog State
const showTemplatesDialog = ref(false);
const isFetchingTemplates = ref(false);
const tab = ref("initial_update");
const templateKeys = ["initial_update", "action_update", "resolution"];
const templates = ref({
  initial_update: "Loading...",
  action_update: "Loading...",
  resolution: "Loading...",
});

/**
 * Fetches incident templates from the backend and opens the dialog.
 */
async function openTemplatesDialog() {
  isFetchingTemplates.value = true;
  showTemplatesDialog.value = true;

  try {
    const response = await axios.get(
      `${API_BASE_URL}/showing_the_template_and_which_bu_is_impacted_to_frontend`
    );

    if (response.data.status === "success") {
      templates.value = response.data.templates;
    } else {
      throw new Error(response.data.error || "Failed to load templates.");
    }
  } catch (error) {
    console.error("Error fetching templates:", error);
    $q.notify({
      color: "negative",
      message: `Failed to load templates: ${error.message}`,
      icon: "report_problem",
    });
    showTemplatesDialog.value = false;
  } finally {
    isFetchingTemplates.value = false;
  }
}

/**
 * Copies the provided text to the clipboard and shows a notification.
 */
function copyTemplate(text) {
  copyToClipboard(text)
    .then(() => {
      $q.notify({
        color: "positive",
        message: "Template copied to clipboard",
        icon: "content_copy",
        position: "top",
      });
    })
    .catch(() => {
      $q.notify({
        color: "negative",
        message: "Could not copy text.",
        icon: "warning",
      });
    });
}

/**
 * Utility function to create a delay.
 */
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Triggers a sequence of API calls to refresh all system data.
 */
async function triggerAllApis() {
  if (isRefreshing.value) return;
  isRefreshing.value = true;

  const showNotification = $q.notify({
    group: false,
    timeout: 0,
    spinner: true,
    message: "Starting refresh...",
    color: "info",
  });

  try {
    const steps = [
      {
        msg: "Refreshing HostMonitor demo data (Charlie + Delta)",
        url: `${API_BASE_URL}/refresh_hostmonitor_report`,
      },
      {
        msg: "Refreshing PRTG alert demo data",
        url: `${API_BASE_URL}/refresh_prtg_alerts_from_pagerduty`,
      },
      {
        msg: "Refreshing JKB demo data",
        url: `${API_BASE_URL}/refresh_all_jkb`,
      },
    ];

    for (const step of steps) {
      showNotification({
        spinner: true,
        message: `${step.msg}...`,
        color: "info",
        icon: "sync",
      });

      await sleep(1);

      try {
        await axios.get(step.url);
        showNotification({
          spinner: false,
          message: `${step.msg} - Finished`,
          color: "green-7",
          icon: "check",
        });
      } catch (error) {
        console.warn(`An error occurred during '${step.msg}':`, error.message);
        showNotification({
          spinner: false,
          message: `${step.msg} - Failed (Skipping)`,
          color: "orange-8",
          icon: "warning",
        });
      }

      await sleep(500);
    }

    lastRefreshed.value = new Date().toLocaleTimeString();

    showNotification({
      icon: "cloud_done",
      spinner: false,
      message: "All data sources refreshed successfully!",
      color: "positive",
      timeout: 3000,
    });
  } catch (error) {
    console.error("A critical error occurred during the refresh sequence:", error);
    showNotification({
      type: "negative",
      icon: "error",
      spinner: false,
      message: `A critical step failed: ${error.message || "Check console."}`,
      timeout: 5000,
    });
  } finally {
    isRefreshing.value = false;
  }
}

onMounted(() => {
  triggerAllApis();
});
</script>

<style scoped>
.templates-dialog {
  border-radius: 12px;
}

/* The template text is meant to be read across the room before it is copied,
   so it stays large - but not the 1.6em it was, which forced a scroll. */
.template-body {
  margin: 0;
  padding: 16px;
  background: var(--app-surface-muted);
  border: 1px solid var(--app-border);
  border-radius: 8px;
  font-size: 15px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: var(--app-ink);
}
</style>
