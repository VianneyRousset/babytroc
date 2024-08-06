import { PrismaClient } from "@prisma/client";
import { verifyToken } from "~/server/utils/token";

const prisma = new PrismaClient();

// Create a loan based on the selected loanRequest
// TODO check user is the owner

export default defineEventHandler(async (event) => {

  const { userId } = await verifyToken(getCookie(event, "token"));

  const itemId = getRouterParam(event, "itemId");
  const borrowerId = getRouterParam(event, "borrowerId");

  const loanRequest = await prisma.loanRequest.delete({
    where: {
      itemId_borrowerId: {
        itemId: itemId as string,
        borrowerId: borrowerId as string,
      }
    }
  })

  return {
    loanRequest: loanRequest,
  };
});
