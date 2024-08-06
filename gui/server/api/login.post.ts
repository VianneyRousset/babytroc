import * as argon2 from "argon2";
import { PrismaClient } from "@prisma/client";
import { createToken } from "~/server/utils/token";

const config = useRuntimeConfig();
const prisma = new PrismaClient();

// A POST on /api/login check the given user and password and return a tokenin
// in case of success

export default defineEventHandler(async (event) => {
  // read POST body
  const body = await readBody(event);

  // check for required fields
  if (body.email === undefined || body.password === undefined) {
    throw createError({
      statusCode: 400,
      statusMessage: "Missing email or password",
    });
  }

  // retrieve user from database
  const user = await prisma.user.findUnique({
    where: {
      email: body.email,
    },
  });

  // check password
  if (
    user === null ||
    !(await argon2.verify(user.password, body.password, config.hashingConfig))
  ) {
    throw createError({
      statusCode: 401,
      statusMessage: "Invalid email or password",
    });
  }

  return {
    token: await createToken(user.id, user.isAdmin),
  };
});


