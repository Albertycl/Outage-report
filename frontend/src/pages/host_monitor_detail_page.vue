<template>
  <div class="app-container">
    <q-table
      :rows="list_of_host_monitor_detail_for_each_infra"
      :columns="columns"
      row-key="infra_name"
      :pagination="initialPagination"
    >
      <!-- Custom title with indentation -->
      <template v-slot:top>
        <div class="table-head">
          <div class="table-head__title">HostMonitor Alert Detail</div>
          <div class="table-head__sub">
            {{ infra_name.toUpperCase() }} &middot; {{ hostmonitor_ip }}
          </div>
        </div>
      </template>
    </q-table>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from "vue"; // <-- 1. Import computed
import { useQuasar } from "quasar";
import axios from "axios";
import { useRoute } from "vue-router";

import { API_BASE_URL } from "src/config/api";
const $q = useQuasar();
const route = useRoute();
const infra_name = route.params.infra_name;
const hostmonitor_ip = route.params.hostmonitor_ip;
const list_of_host_monitor_detail_for_each_infra = ref([]);

// 2. Change `columns` from a `const` array to a `computed` property
const columns = computed(() => {
  // Define the columns that are always present
  const allColumns = [
    {
      name: "infra_name",
      label: "Infra Name",
      align: "center",
      field: (row) => row.infra_name,
      sortable: true,
    },
    {
      name: "hostmonitor_ip",
      label: "Hostmonitor_ip",
      align: "center",
      field: (row) => row.hostmonitor_ip,
      sortable: true,
    },
    {
      name: "timestamp",
      label: "Timestamp",
      align: "center",
      field: (row) => row.timestamp,
      sortable: true,
    },
    // The conditional column will be inserted here
    {
      name: "alert_name",
      label: "Alert Name",
      align: "center",
      field: (row) => row.alert_name,
      sortable: true,
    },
  ];

  // 3. Check the route parameter
  if (
    route.params.hostmonitor_ip &&
    route.params.hostmonitor_ip.endsWith(".82")
  ) {
    // 4. If it matches, insert the special column at the correct index (e.g., index 3)
    allColumns.splice(3, 0, {
      name: "in_ltm_or_not_in_ltm",
      label: "In LTM",
      align: "center",
      field: (row) => row.in_ltm_or_not_in_ltm,
      sortable: true,
    });
  }

  // 5. Return the final array of columns
  return allColumns;
});

const initialPagination = reactive({
  sortBy: "infra_name",
  descending: false,
  page: 1,
  rowsPerPage: 0, // Show all rows
});

async function a10_get_hostmonitor_alerts_detail() {
  try {
    const url = `${API_BASE_URL}/query_hostmonitor_alert_detail/${infra_name}/${hostmonitor_ip}`;
    const { data } = await axios.get(url);
    list_of_host_monitor_detail_for_each_infra.value = data;
  } catch (error) {
    $q.notify({
      type: "negative",
      icon: "error",
      message: `Failed to load details for "${infra_name}": ${error.message || error}`,
    });
  }
}

a10_get_hostmonitor_alerts_detail();
</script>

<style scoped>

/* The table title was a solid black / green / orange bar - the only filled
   heading in the app. It reads as part of the table now. */
.table-head {
  width: 100%;
  padding: 4px 0 12px;
}

.table-head__title {
  font-size: 16px;
  font-weight: 650;
  letter-spacing: -0.01em;
  color: var(--app-ink);
}

.table-head__sub {
  margin-top: 2px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--app-ink-subtle);
}
</style>
