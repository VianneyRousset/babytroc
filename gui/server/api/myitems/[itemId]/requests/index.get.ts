import { PrismaClient } from "@prisma/client";
import { verifyToken } from "~/server/utils/token";

const prisma = new PrismaClient();

// Get all the requests of the item given in path

export default defineEventHandler(async (event) => {

  const { userId } = await verifyToken(getCookie(event, "token"));

  const itemId = getRouterParam(event, "itemId");

  // get item
  const item = await prisma.item.findUnique({
    where: {
      id: itemId,
      ownerId: userId,
    },
    include: {
      loanRequests: {
        include: {
          borrower: {
            select: {
              id: true,
              name: true,
            }
          }
        }
      },
    }
  });

  return {
    loanRequests: item?.loanRequests,
  };
});
