import { PrismaClient } from "@prisma/client";
import { verifyToken } from "~/server/utils/token";

const prisma = new PrismaClient();

// Get the list of all the items

export default defineEventHandler(async (event) => {

  await verifyToken(getCookie(event, "token"));

  // get all districts
  const districts = await prisma.district.findMany({});

  return {
    districts: districts,
  };
});
