import { Prisma, PrismaClient, Loan } from "@prisma/client";
import { verifyToken } from "~/server/utils/token";

const prisma = new PrismaClient();

// Create a loan based on the selected loanRequest
// TODO check item is owned by user
// TODO remove loanRequest

export default defineEventHandler(async (event) => {

  const { userId } = await verifyToken(getCookie(event, "token"));

  const itemId = getRouterParam(event, "itemId");
  const borrowerId = getRouterParam(event, "borrowerId");

  // create new load if no loan link to the item is unfinished (endAt = NULL) or
  // has a endAt date after now().
  const loan = await prisma.$queryRaw<Loan[]>(Prisma.sql`
    INSERT INTO public."Loan"("itemId", "borrowerId", "startAt", "endAt")
      SELECT ${itemId}, ${borrowerId}, NOW(), NULL
      WHERE NOT EXISTS(
        SELECT 1
        FROM public."Loan"
        WHERE("itemId" = ${itemId} AND "endAt" IS NULL) OR ("itemId" = ${itemId} AND "endAt" > NOW())
      )
      RETURNING *
  `);

  if (loan.length == 0) {
    throw createError({
      statusCode: 400,
      statusMessage: "Another loan is active.",
    })
  }

  const loanRequest = await prisma.loanRequest.delete({
    where: {
      itemId_borrowerId: {
        itemId: itemId as string,
        borrowerId: borrowerId as string,
      }
    }
  })

  return {
    loan: loan[0],
    loanRequest: loanRequest,
  };
});
