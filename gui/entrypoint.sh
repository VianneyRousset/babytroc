#!/usr/bin/env sh

# Run Prisma migrations
npx prisma migrate dev

# Optionally seed the database
npx prisma db seed

# Cleanup garbage
rm -f /tmp/nitro/worker-*.sock

# Start the Nuxt.js application
npm run dev
