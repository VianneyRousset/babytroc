#!/usr/bin/env ts-node

import { PrismaClient, Prisma } from "@prisma/client";
import * as argon2 from "argon2";
import config from '../config'

const prisma = new PrismaClient();

type User = {
  name: string,
  email: string,
  password: string,
};

async function ensureUser(user: User) {
  try {
    await prisma.user.create({
      data: {
        email: user.email,
        name: user.name,
        password: await argon2.hash(user.password, config.hashingConfig),
      }
    });
    console.log(`✔️ User ${user.email} created.`);
  } catch (error) {
    if (error.code == "P2002") {
      console.log(`✔️ User ${user.email} already exists.`);
    } else {
      console.error(`❌Failed to create user ${user.email}.`);
      throw error;
    }
  }

}

async function main() {

  await ensureUser({
    email: "alice",
    name: "Alice",
    password: "xxx",
  });

  await ensureUser({
    email: "bob",
    name: "Bob",
    password: "xxx",
  });

}

await main();
