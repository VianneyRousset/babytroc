import { PrismaClient } from "@prisma/client";
import { verifyToken } from "~/server/utils/token";

const prisma = new PrismaClient();

// Get info of the item given in path

export default defineEventHandler(async (event) => {

  const { userId } = await verifyToken(getCookie(event, "token"));

  const itemId = getRouterParam(event, "itemId");

  // get item
  const item = await prisma.item.findUnique({
    where: { id: itemId },
    include: {
      owner: {
        select: {
          id: true,
          name: true,
          createdAt: true,
        }
      },
      _count: {
        select: {
          loanRequests: {
            where: {
              borrowerId: userId,
            }
          }
        }
      }
    }
  }) as any;

  if (item === null) {
    throw createError({
      statusCode: 404,
      statusMessage: "Item not found",
    });
  }

  item.requested = item._count.loanRequests > 0;
  delete item._count;

  return {
    item: item,
  };
});
