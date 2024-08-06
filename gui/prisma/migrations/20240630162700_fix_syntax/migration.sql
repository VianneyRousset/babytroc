/*
  Warnings:

  - You are about to drop the column `EndAt` on the `Loan` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "Loan" DROP COLUMN "EndAt",
ADD COLUMN     "endAt" TIMESTAMP(3);
