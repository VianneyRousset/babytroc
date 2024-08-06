import { Prisma, PrismaClient, Loan } from "@prisma/client";
import { verifyToken } from "~/server/utils/token";

const prisma = new PrismaClient();

// Get info on the loan given by path
// TODO check loan is owned by user

export default defineEventHandler(async (event) => {

  const { userId } = await verifyToken(getCookie(event, "token"));

  const loanId = Number(getRouterParam(event, "loanId"));

  // update loan endAt date
  const result = await prisma.$executeRaw(Prisma.sql`
    UPDATE public."Loan"
    SET "endAt" = NOW()
    WHERE id = ${loanId} 
    AND "endAt" IS NULL
    AND "startAt" < NOW()
  `);

  if (result == 0) {
    throw createError({
      statusCode: 400,
      statusMessage: "Failed to terminate loan. The loan might not exist, or already terminated or with a startDate in the future."
    })
  }

  return {
    success: true,

  };
});
