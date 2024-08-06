import { PrismaClient } from "@prisma/client";
import { verifyToken } from "~/server/utils/token";

const prisma = new PrismaClient();

// Get info of the item given in path
// TODO improve SQL query to use the now() of the database

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
        select: {
          createdAt: true,
          borrower: {
            select: {
              id: true,
              name: true,
            }
          }
        },
      },
      loans: {
        where: {
          endAt: null,
        },
        include: {
          borrower: {
            select: {
              id: true,
              name: true,
            },
          },
        },
      },
    },
  }) as any;

  item.activeLoan = item.loans[0] || null;
  delete item.loans;

  return {
    item: item,
  };
});
