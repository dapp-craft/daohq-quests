-- Disable the enforcement of foreign-keys constraints
PRAGMA foreign_keys = off;
-- Drop "CollectedCoins" table
DROP TABLE `CollectedCoins`;
-- Drop "CollectedCoinsHistory" table
DROP TABLE `CollectedCoinsHistory`;
-- Create "TodayCoins" table
CREATE TABLE `TodayCoins` (
  `id` integer NULL,
  `user` integer NULL,
  `coin` integer NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `0` FOREIGN KEY (`coin`) REFERENCES `Coins` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT `1` FOREIGN KEY (`user`) REFERENCES `Users` (`address`) ON UPDATE NO ACTION ON DELETE NO ACTION
);
-- Create index "TodayCoins_user_coin" to table: "TodayCoins"
CREATE UNIQUE INDEX `TodayCoins_user_coin` ON `TodayCoins` (`user`, `coin`);
-- Create "ResetCoinsHistory" table
CREATE TABLE `ResetCoinsHistory` (
  `id` integer NULL,
  `user` integer NULL,
  `timestamp` integer NULL,
  `collected_coins` integer NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `0` FOREIGN KEY (`user`) REFERENCES `Users` (`address`) ON UPDATE NO ACTION ON DELETE NO ACTION
);
-- Enable back the enforcement of foreign-keys constraints
PRAGMA foreign_keys = on;
