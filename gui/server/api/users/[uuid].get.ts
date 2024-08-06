import { PrismaClient } from "@prisma/client";
import { verifyToken } from "~/server/utils/token";

const prisma = new PrismaClient();

export default defineEventHandler(async (event) => {
  const token_userid = await verifyToken(getCookie(event, "token"));
  const route_userid = getRouterParam(event, "uuid");

  if (token_userid !== route_userid) {
    throw createError({
      statusCode: 401,
      statusMessage: "Unauthorized",
    });
  }

  // retrieve user from database
  const user = await prisma.user.findUnique({
    where: {
      id: route_userid,
    },
  });

  if (user === null) {
    throw createError({
      statusCode: 404,
      statusMessage: "User not found",
    });
  }

  return {
    id: user.id,
    email: user.email,
    name: user.name,
    creation_date: user.creation_date,
  };
});
