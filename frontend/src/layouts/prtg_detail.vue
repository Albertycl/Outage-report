<template>
  <div class="app-container">
    <q-table
      :rows="list_of_prtg_alerts"
      :columns="columns"
      row-key="id"
      :pagination="initialPagination"
    >
      <template v-slot:top>
        <div class="table-head">
          <div class="table-head__title">PRTG Alerts</div>
          <div class="table-head__sub">{{ infraName.toUpperCase() }}</div>
        </div>
      </template>

      <template v-slot:body-cell-title="props">
        <q-td :props="props">
          <div class="text-wrap">
            {{ props.row.title }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-sensor_id="props">
        <q-td :props="props">
          <a :href="getSensorLink(props.row.sensor_id)" target="_blank">
            {{ props.row.sensor_id }}
          </a>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useRoute } from "vue-router";
import axios from "axios";

import { API_BASE_URL } from "src/config/api";
import { prtgSensorLink } from "src/config/infra";
// 1. 拿到路由參數
const route = useRoute();
const infraName = route.params.infra_name;

// 2. 資料和表格設定
const list_of_prtg_alerts = ref([]);

const columns = [
  {
    name: "timestamp",
    label: "Timestamp",
    align: "left",
    field: (row) => row.timestamp,
    sortable: true,
  },
  {
    name: "title",
    label: "Alert Title",
    align: "left",
    field: (row) => row.title,
    sortable: true,
  },
  {
    name: "sensor_id",
    label: "Sensor ID",
    align: "center",
    field: (row) => row.sensor_id,
    sortable: true,
  },
  {
    name: "infra_name",
    label: "Infrastructure",
    align: "center",
    field: (row) => row.whicih_infra,
    sortable: true,
  },
];

const initialPagination = reactive({
  sortBy: "timestamp",
  descending: true,
  page: 1,
  rowsPerPage: 10,
});

// Function to generate the sensor link
const getSensorLink = (sensorId) => prtgSensorLink(infraName, sensorId) || "#";

// 3. 拿參數呼叫 API
async function fetchPrtgAlerts() {
  try {
    const url = `${API_BASE_URL}/frontend_query_prtg_detail/${infraName}`;
    const res = await axios.get(url);
    list_of_prtg_alerts.value = res.data;
  } catch (err) {
    console.error("Error fetching PRTG alerts:", err);
  }
}

// 4. onMounted 時觸發
onMounted(() => {
  fetchPrtgAlerts();
});
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
.text-wrap {
  white-space: normal;
}
</style>
