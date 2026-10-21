<template>
  <div class="q-pa-md" style="max-width: 80%; margin: 0 auto; overflow-x: auto">
    <q-table
      :rows="list_of_host_monitor_summary_alerts"
      :columns="columns"
      row-key="sensor_id"
      :pagination="initialPagination"
    >
      <!-- your existing alerts-count link slot -->
      <template v-slot:body-cell-number_of_total_alerts="props">
        <q-td style="text-align: center">
          <router-link
            :to="`/details/${props.row.infra_name}`"
            class="text-primary text-weight-bold"
          >
            {{ props.row.number_of_total_alerts }}
          </router-link>
        </q-td>
      </template>

      <!-- Custom title with indentation -->
      <template v-slot:top>
        <div class="bg-black text-white text-h6 q-pa-sm q-pl-lg">PRTG Alert Summary</div>
      </template>

      <!-- make New Connection a hyperlink -->
      <template v-slot:body-cell-new_connection="props">
        <q-td style="text-align: center">
          <a :href="props.row.prtg_link" target="_blank" rel="noopener">
            {{ props.row.lastvalue }}
          </a>
        </q-td>
      </template>

      <template v-slot:body-cell-down_count="props">
        <q-td style="text-align: center">
          <router-link
            :to="`/prtg_detail/${props.row.infra_name}`"
            class="text-primary text-weight-bold"
          >
            {{ props.row.down_count }}
          </router-link>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import axios from "axios";

import { API_BASE_URL } from "src/config/api";
const list_of_host_monitor_summary_alerts = ref([]);

const columns = [
  {
    name: "infra_name",
    label: "Infra Name",
    align: "center",
    field: (r) => r.infra_name,
    sortable: true,
  },
  {
    name: "timestamp",
    label: "Timestamp",
    align: "center",
    field: (r) => r.timestamp,
    sortable: true,
  },
  {
    name: "new_connection",
    label: "New Connection",
    align: "center",
    field: (r) => r.lastvalue,
    sortable: true,
  },
  {
    name: "down_count",
    label: "Down Count",
    align: "center",
    field: (r) => r.down_count,
    sortable: true,
  },
];

const initialPagination = reactive({
  sortBy: "timestamp",
  descending: true,
  page: 1,
  rowsPerPage: 10,
});

async function a10_get_hostmonitor_alerts_summary() {
  try {
    // 1. fire the “warm-up” request and wait for it to complete
    // const warmUpResp = await axios.get(`${API_BASE_URL}/prtg_summary`);
    // // (optional) you can inspect warmUpResp.status or data here
    // console.log("warm-up done:", warmUpResp.status);

    // 2. now fire the real request and wait for *that* to complete
    const realResp = await axios.get(
      `${API_BASE_URL}/frontend_query_prtg_summary`
    );
    list_of_host_monitor_summary_alerts.value = realResp.data;
  } catch (err) {
    console.error(err);
  }
}
a10_get_hostmonitor_alerts_summary();
</script>
