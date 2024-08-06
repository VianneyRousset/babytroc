/*
  Warnings:

  - You are about to drop the column `updatedAt` on the `Item` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "Item" DROP COLUMN "updatedAt";

-- CreateTable
CREATE TABLE "LoanRequest" (
    "itemId" TEXT NOT NULL,
    "borrowerId" TEXT NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "LoanRequest_itemId_borrowerId_key" ON "LoanRequest"("itemId", "borrowerId");

-- AddForeignKey
ALTER TABLE "LoanRequest" ADD CONSTRAINT "LoanRequest_itemId_fkey" FOREIGN KEY ("itemId") REFERENCES "Item"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "LoanRequest" ADD CONSTRAINT "LoanRequest_borrowerId_fkey" FOREIGN KEY ("borrowerId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
