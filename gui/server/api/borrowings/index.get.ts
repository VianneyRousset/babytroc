import { PrismaClient } from "@prisma/client";
import { verifyToken } from "~/server/utils/token";
import { booleanQueryParam } from "~/server/utils/query";
import { z } from "zod";

const prisma = new PrismaClient();

// Get the loans where the user is the borrower

export default defineEventHandler(async (event) => {

  const { userId } = await verifyToken(getCookie(event, "token"));

  const userSchema = z.object({
    active: booleanQueryParam,
  })

  const params = await getValidatedQuery(event, query => userSchema.parse(query));

  if (params.active) {

    // get all loans
    const loans = await prisma.loan.findMany({
      where: {
        borrowerId: userId,
        endAt: null,
      },
      include: {
        item: true,
      },
    });

    return {
      loans: loans,
    };

  }

  // get all loans
  const loans = await prisma.loan.findMany({
    where: {
      borrowerId: userId,
    },
    include: {
      item: true,
    },
  });



  return {
    loans: loans,
  };

});
