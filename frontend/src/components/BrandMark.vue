<template>
  <!-- The product mark: a signal radiating from a source, with an alert pip.
       Drawn as inline SVG rather than an image file so it stays sharp on the
       wall screen and so the favicon can be generated from the same shapes. -->
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 32 32"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    role="img"
    aria-label="Outage Detector"
  >
    <defs>
      <linearGradient :id="gradientId" x1="0" y1="0" x2="32" y2="32"
        gradientUnits="userSpaceOnUse">
        <stop stop-color="#3B82F6" />
        <stop offset="1" stop-color="#1D4ED8" />
      </linearGradient>
    </defs>

    <rect width="32" height="32" rx="7.5" :fill="`url(#${gradientId})`" />

    <!-- source -->
    <circle cx="13" cy="19" r="2.6" fill="#fff" />
    <!-- the signal going out from it -->
    <path d="M19.4 19A6.4 6.4 0 0 0 13 12.6" stroke="#fff" stroke-width="2"
      stroke-linecap="round" opacity="0.9" />
    <path d="M24.2 19A11.2 11.2 0 0 0 13 7.8" stroke="#fff" stroke-width="2"
      stroke-linecap="round" opacity="0.45" />
    <!-- the thing being detected -->
    <circle cx="24.5" cy="7.5" r="3.6" fill="#F59E0B" stroke="#1D4ED8"
      stroke-width="1.6" />
  </svg>
</template>

<script setup>
defineProps({
  size: { type: [Number, String], default: 32 },
});

// Two marks on one page would otherwise share a gradient id, and the second
// would inherit the first one's stops.
const gradientId = `brand-mark-${Math.random().toString(36).slice(2, 9)}`;
</script>
