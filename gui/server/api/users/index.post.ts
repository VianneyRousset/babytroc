import { PrismaClient, Prisma } from "@prisma/client";
import * as argon2 from "argon2";

const config = useRuntimeConfig();
const prisma = new PrismaClient();

export default defineEventHandler(async (event) => {

  // read POST body
  const body = await readBody(event);

  // check for required fields
  if (body.name === undefined) {
    throw createError({
      statusCode: 400,
      statusMessage: "Missing name",
      data: {
        userMessage: "Missing name.",
        errorCode: 1,
      }
    });
  }

  if (body.email === undefined) {
    throw createError({
      statusCode: 400,
      statusMessage: "Missing email",
      data: {
        userMessage: "Missing email.",
        errorCode: 2,
      }
    });
  }

  if (body.password === undefined) {
    throw createError({
      statusCode: 400,
      statusMessage: "Missing password",
      data: {
        userMessage: "Missing password.",
        errorCode: 3,
      }
    });
  }

  // add user to database
  try {
    return await prisma.user.create({
      data: {
        name: body.name,
        email: body.email,
        password: await argon2.hash(body.password, config.hashingConfig),
      },
    });
  } catch (error: unknown) {

    if (error instanceof Prisma.PrismaClientKnownRequestError) {

      if (error.code === 'P2002') {
        throw createError({
          statusCode: 400,
          statusMessage: "User email exists",
          data: {
            userMessage: `The user "${body.email}" already exists.`,
            errorCode: 4,
          }
        });
      }

    }

    throw error;
  }
});
