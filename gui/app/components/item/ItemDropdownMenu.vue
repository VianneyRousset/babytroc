<script setup lang="ts">
import { ShieldAlert } from 'lucide-vue-next'
</script>

<template>
  <DropdownMenu>
    <!-- Report -->
    <DropdownMenuItem class="red">
      <ShieldAlert
        :size="32"
        :stroke-width="2"
      />
      <div>Signaler</div>
    </DropdownMenuItem>
  </DropdownMenu>
</template>
