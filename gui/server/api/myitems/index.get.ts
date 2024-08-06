import { PrismaClient } from "@prisma/client";
import { verifyToken } from "~/server/utils/token";

const prisma = new PrismaClient();

// Get the list of all the items owned by the user

export default defineEventHandler(async (event) => {

  const { userId } = await verifyToken(getCookie(event, "token"));

  // get all items
  const items = await prisma.item.findMany({
    where: {
      ownerId: userId,
    },
    include: {
      loans: {
        orderBy: {
          startAt: "desc",
        },
        take: 1,
      },
      _count: {
        select: {
          loanRequests: true,
        }
      }
    },
  }) as any[];

  items.map((item) => {
    const hasActiveLoan = item.loans.length > 0 && item.loans[0].endAt === null;
    item.activeLoan = hasActiveLoan ? item.loans[0] : null;
    delete item.loans;
    return item;
  });


  return {
    items: items,
  };
});
