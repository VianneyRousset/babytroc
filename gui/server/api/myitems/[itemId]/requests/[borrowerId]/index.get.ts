import { PrismaClient } from "@prisma/client";
import { verifyToken } from "~/server/utils/token";

const prisma = new PrismaClient();

// Get info on the loanRequest given by (itemId, borrowerId) in the url
// TODO check user 

export default defineEventHandler(async (event) => {

  const { userId } = await verifyToken(getCookie(event, "token"));

  const itemId = getRouterParam(event, "itemId");
  const borrowerId = getRouterParam(event, "borrowerId");

  // get loanRequest
  const loanRequest = await prisma.loanRequest.findUnique({
    where: {
      itemId_borrowerId: {
        itemId: itemId as string,
        borrowerId: borrowerId as string,
      }
    },
    include: {
      borrower: {
        select: {
          id: true,
          name: true,
        },
      },
    },
  });

  return {
    loanRequest: loanRequest,
  };
});
