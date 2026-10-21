<template>
  <!-- The 404 used to be a full-bleed blue field with a 30vh numeral. It is a
       normal page now: say what happened, and give the way back. -->
  <div class="notfound">
    <div class="notfound__code">404</div>
    <div class="notfound__title">Page not found</div>
    <div class="notfound__body">
      That address does not match anything in the dashboard.
    </div>
    <q-btn
      no-caps
      unelevated
      color="primary"
      icon="arrow_back"
      label="Back to dashboard"
      to="/"
      class="q-mt-lg"
    />
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'ErrorNotFound'
})
</script>

<style scoped>
.notfound {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
  padding: 24px;
  text-align: center;
}

.notfound__code {
  font-size: 64px;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.03em;
  color: var(--app-border-strong);
}

.notfound__title {
  margin-top: 12px;
  font-size: 20px;
  font-weight: 650;
  color: var(--app-ink);
}

.notfound__body {
  margin-top: 6px;
  font-size: 14px;
  color: var(--app-ink-subtle);
}
</style>
