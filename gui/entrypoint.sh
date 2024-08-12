#!/usr/bin/env sh

# Cleanup garbage
rm -f /tmp/nitro/worker-*.sock

# Start the Nuxt.js application
npm run dev
