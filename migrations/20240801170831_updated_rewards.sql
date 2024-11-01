-- Rename a column from "token" to "collection"
ALTER TABLE `Rewards` RENAME COLUMN `token` TO `collection`;
-- Add column "blockchain_id" to table: "Rewards"
ALTER TABLE `Rewards` ADD COLUMN `blockchain_id` integer NULL;
