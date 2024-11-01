-- Disable the enforcement of foreign-keys constraints
PRAGMA foreign_keys = off;
-- Create "new_TodayCoins" table
CREATE TABLE `new_TodayCoins` (
  `id` integer NULL,
  `user` integer NULL,
  `coin` integer NULL,
  `is_collected` boolean NULL DEFAULT False,
  PRIMARY KEY (`id`),
  CONSTRAINT `0` FOREIGN KEY (`coin`) REFERENCES `Coins` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT `1` FOREIGN KEY (`user`) REFERENCES `Users` (`address`) ON UPDATE NO ACTION ON DELETE NO ACTION
);
-- Copy rows from old table "TodayCoins" to new temporary table "new_TodayCoins"
INSERT INTO `new_TodayCoins` (`id`, `user`, `coin`) SELECT `id`, `user`, `coin` FROM `TodayCoins`;
-- Drop "TodayCoins" table after copying rows
DROP TABLE `TodayCoins`;
-- Rename temporary table "new_TodayCoins" to "TodayCoins"
ALTER TABLE `new_TodayCoins` RENAME TO `TodayCoins`;
-- Create index "TodayCoins_user_coin" to table: "TodayCoins"
CREATE UNIQUE INDEX `TodayCoins_user_coin` ON `TodayCoins` (`user`, `coin`);
-- Enable back the enforcement of foreign-keys constraints
PRAGMA foreign_keys = on;
