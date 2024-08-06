import { PrismaClient } from "@prisma/client";
import { verifyToken } from "~/server/utils/token";

const prisma = new PrismaClient();

export default defineEventHandler(async (event) => {

  const { isAdmin } = await verifyToken(getCookie(event, "token"));

  if (!isAdmin) {
    throw createError({
      statusCode: 401,
      statusMessage: "Unauthorized",
    });
  }

  // get all items
  const users = await prisma.user.findMany({})

  return {
    users: users,
  };
});
