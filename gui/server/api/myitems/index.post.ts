import { PrismaClient } from "@prisma/client";
import { verifyToken } from "~/server/utils/token";

const prisma = new PrismaClient();

// Create a new item owned by the user.
//
// Body fields:
// - name: Name of the item
// - description: Optional description of the item.
//
// Error codes:
// - 1: Missing name

export default defineEventHandler(async (event) => {

  // check credentials
  const { userId } = await verifyToken(getCookie(event, "token"));

  // read POST body
  const body = await readBody(event);

  // check for required fields
  if (body?.name === undefined) {
    throw createError({
      statusCode: 400,
      statusMessage: "Missing name",
      data: {
        errorCode: 1,
      }
    });
  }

  // add item to database
  return await prisma.item.create({
    data: {
      ownerId: userId,
      name: body.name,
      description: body.description ?? null,
      image: body.image,
    },
  });

});
