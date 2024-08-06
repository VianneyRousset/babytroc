import { Prisma, PrismaClient, Loan } from "@prisma/client";
import { verifyToken } from "~/server/utils/token";

const prisma = new PrismaClient();

// Get all the loan where the item owner is the user

export default defineEventHandler(async (event) => {

  const { userId } = await verifyToken(getCookie(event, "token"));

  // select all loan where the owner of the item is the user
  const loans = await prisma.$queryRaw<Loan[]>(Prisma.sql`
    SELECT public."Loan".id, public."Loan"."itemId", public."Loan"."borrowerId", public."Loan"."startAt", public."Loan"."endAt" 
    FROM public."Loan"
    JOIN public."Item" ON "Loan"."itemId" = public."Item".id
    WHERE public."Item"."ownerId" = ${userId}
  `);


  return {
    loans: loans,
  };
});
