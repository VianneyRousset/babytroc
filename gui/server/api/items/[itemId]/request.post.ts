import { PrismaClient } from "@prisma/client";
import { verifyToken } from "~/server/utils/token";

const prisma = new PrismaClient();

// Create a loanRequest with the user a borrower and the item given in path

export default defineEventHandler(async (event) => {

  const { userId } = await verifyToken(getCookie(event, "token"));

  const itemId = getRouterParam(event, "itemId");

  // get item
  const { item } = await prisma.item.findUnique({
    where: { id: itemId },
  }) as any;

  // check item is not owned by the user
  // TODO need for lock ?
  /*
  if (item.ownerId == userId) {
    throw createError({
      statusCode: 400,
      statusMessage: "Cannot request an item owned by user.",
    })
  }
  */

  // create a loanRequest
  const loanRequest = await prisma.loanRequest.create({
    data: {
      itemId: itemId as string,
      borrowerId: userId,
    },
  })

  return {
    request: loanRequest,
  };
});
