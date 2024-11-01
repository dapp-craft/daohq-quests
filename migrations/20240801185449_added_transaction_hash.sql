-- Add column "transaction_hash" to table: "CollectedRewards"
ALTER TABLE `CollectedRewards` ADD COLUMN `transaction_hash` varchar NULL;
