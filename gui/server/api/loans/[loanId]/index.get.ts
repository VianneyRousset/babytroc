import { PrismaClient } from "@prisma/client";
import { verifyToken } from "~/server/utils/token";

const prisma = new PrismaClient();

// Get info on the loan given by path

export default defineEventHandler(async (event) => {

  const { userId } = await verifyToken(getCookie(event, "token"));

  const loanId = Number(getRouterParam(event, "loanId"));

  // get item
  const loan = await prisma.loan.findUnique({
    where: {
      id: loanId,
    },
    select: {
      id: true,
      startAt: true,
      endAt: true,
      borrower: {
        select: {
          id: true,
          name: true,
        },
      },
      item: true,
    },
  });

  if (loan?.item.ownerId !== userId) {
    throw createError({
      statusCode: 500,
      statusMessage: "Forbidden",
    })
  }

  return {
    loan: loan,
  };
});
