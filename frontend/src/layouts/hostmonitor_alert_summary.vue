<template>
  <div class="hostmonitor-summary-container">
    <div class="q-pa-md">
      <q-table
        :rows="list_of_host_monitor_summary_alerts"
        :columns="columns"
        :row-key="rowKey"
        :pagination="initialPagination"
        class="hostmonitor-table"
        flat
        bordered
      >
        <!-- Custom title with better styling -->
        <template v-slot:top>
          <div class="table-header">
            <q-icon name="monitor" size="md" class="q-mr-sm" />
            <span class="table-title">HostMonitor Alert Summary</span>
          </div>
        </template>

        <!-- Custom cell for total alerts with router link -->
        <template v-slot:body-cell-number_of_total_alerts="props">
          <q-td :props="props" class="text-center">
            <router-link
              :to="`/host_monitor_detail_page/${props.row.infra_name}/${props.row.hostmonitor_ip}`"
              class="alert-link"
            >
              <q-chip
                :color="getAlertColor(props.row.number_of_total_alerts)"
                text-color="white"
                :label="props.row.number_of_total_alerts"
                clickable
                size="sm"
              />
            </router-link>
          </q-td>
        </template>

        <!-- Custom cell for alert percentage -->
        <template v-slot:body-cell-alert_percentage="props">
          <q-td :props="props" class="text-center">
            <q-badge
              :color="getPercentageColor(props.row.alert_percentage)"
              :label="props.row.alert_percentage + '%'"
              class="percentage-badge"
            />
          </q-td>
        </template>

        <!-- Custom cell for infra name -->
        <template v-slot:body-cell-infra_name="props">
          <q-td :props="props" class="text-center">
            <q-chip
              color="primary"
              text-color="white"
              :label="props.row.infra_name"
              outline
              size="sm"
            />
          </q-td>
        </template>

        <!-- Custom cell for timestamp -->
        <template v-slot:body-cell-timestamp="props">
          <q-td :props="props" class="text-center">
            <div class="timestamp-cell">
              {{ formatTimestamp(props.row.timestamp) }}
            </div>
          </q-td>
        </template>

        <!-- Custom cell for hostmonitor IP -->
        <template v-slot:body-cell-hostmonitor_ip="props">
          <q-td :props="props" class="text-center">
            <code class="ip-address">{{ props.row.hostmonitor_ip }}</code>
          </q-td>
        </template>

        <!-- Loading state -->
        <template v-slot:loading>
          <q-inner-loading showing color="primary" />
        </template>

        <!-- No data state -->
        <template v-slot:no-data="{ icon, message, filter }">
          <div class="full-width row flex-center text-grey q-gutter-sm">
            <q-icon size="2em" name="warning" />
            <span>No HostMonitor alerts found</span>
          </div>
        </template>
      </q-table>
    </div>

    <!-- PRTG Summary Component -->
    <prtg_summary />
  </div>
</template>

<script setup>
import { reactive, ref, computed } from "vue";
import axios from "axios";
import prtg_summary from "./prtg_summary.vue";

import { API_BASE_URL } from "src/config/api";
const list_of_host_monitor_summary_alerts = ref([]);
const loading = ref(false);

// Make a compound key generator to avoid duplicate key warning
const rowKey = (row) => `${row.infra_name}-${row.hostmonitor_ip}`;

const columns = [
  {
    name: "hostmonitor_ip",
    required: true,
    label: "HostMonitor IP",
    align: "center",
    field: (row) => row.hostmonitor_ip,
    sortable: true,
    style: "width: 140px",
  },
  {
    name: "infra_name",
    required: true,
    label: "Infrastructure",
    align: "center",
    field: (row) => row.infra_name,
    sortable: true,
    style: "width: 120px",
  },
  {
    name: "timestamp",
    required: true,
    label: "Last Updated",
    align: "center",
    field: (row) => row.timestamp,
    sortable: true,
    style: "width: 180px",
  },
  {
    name: "alert_percentage",
    required: true,
    label: "Alert %",
    align: "center",
    field: (row) => row.alert_percentage,
    sortable: true,
    style: "width: 100px",
  },
  {
    name: "number_of_total_alerts",
    required: true,
    label: "Total Alerts",
    align: "center",
    field: (row) => row.number_of_total_alerts,
    sortable: true,
    style: "width: 120px",
  },
  {
    name: "number_of_alerts_in_ltm",
    required: true,
    label: "Alerts in LTM",
    align: "center",
    field: (row) => row.number_of_alerts_in_ltm,
    sortable: true,
    style: "width: 130px",
  },
  {
    name: "number_of_alerts_not_in_ltm",
    required: true,
    label: "Alerts not in LTM",
    align: "center",
    field: (row) => row.number_of_alerts_not_in_ltm,
    sortable: true,
    style: "width: 150px",
  },
  {
    name: "total_sensor_for_this_infra",
    required: true,
    label: "Total Sensors",
    align: "center",
    field: (row) => row.total_sensor_for_this_infra,
    sortable: true,
    style: "width: 130px",
  },
];

const initialPagination = reactive({
  sortBy: "hostmonitor_ip",
  descending: false,
  page: 1,
  rowsPerPage: 10, // Show 10 rows per page instead of all
});

// Helper functions for styling
const getAlertColor = (alertCount) => {
  if (alertCount === 0) return "positive";
  if (alertCount <= 5) return "warning";
  return "negative";
};

const getPercentageColor = (percentage) => {
  const percent = parseFloat(percentage);
  if (percent === 0) return "positive";
  if (percent <= 10) return "warning";
  return "negative";
};

const formatTimestamp = (timestamp) => {
  if (!timestamp) return "N/A";
  try {
    const date = new Date(timestamp);
    return date.toLocaleString();
  } catch (error) {
    return timestamp;
  }
};

const a10_get_hostmonitor_alerts_summary = async () => {
  loading.value = true;
  try {
    const url = `${API_BASE_URL}/showing_hostmonitor_alert_summary`;
    const response = await axios.get(url);
    list_of_host_monitor_summary_alerts.value = response.data;
  } catch (error) {
    console.error(`Error fetching HostMonitor alerts:`, error);
    // You might want to show a notification here
  } finally {
    loading.value = false;
  }
};

// Initialize data on component mount
a10_get_hostmonitor_alerts_summary();
</script>

<style scoped>
.hostmonitor-summary-container {
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
}

.hostmonitor-table {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.table-header {
  width: 100%;
  background: linear-gradient(45deg, #4caf50, #66bb6a);
  color: white;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.table-title {
  font-size: 1.1rem;
  font-weight: 600;
}

.alert-link {
  text-decoration: none;
  transition: transform 0.2s ease;
}

.alert-link:hover {
  transform: scale(1.05);
}

.percentage-badge {
  min-width: 50px;
  font-weight: 600;
}

.timestamp-cell {
  font-size: 0.85rem;
  color: #666;
  font-family: monospace;
}

.ip-address {
  background-color: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #2196f3;
  font-weight: 500;
}

/* Responsive design */
@media (max-width: 768px) {
  .hostmonitor-summary-container {
    padding: 0 8px;
  }

  .table-header {
    padding: 12px 16px;
    font-size: 16px;
  }

  .table-title {
    font-size: 1rem;
  }
}

/* Table row hover effect */
.hostmonitor-table :deep(.q-table tbody tr:hover) {
  background-color: #f8f9fa;
}

/* Header styling */
.hostmonitor-table :deep(.q-table thead th) {
  background-color: #f5f5f5;
  color: #333;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.5px;
}

/* Alternating row colors */
.hostmonitor-table :deep(.q-table tbody tr:nth-child(even)) {
  background-color: #fafafa;
}
</style>
