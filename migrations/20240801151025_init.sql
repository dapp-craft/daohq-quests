-- Create "Users" table
CREATE TABLE `Users` (
  `address` varchar NULL,
  PRIMARY KEY (`address`)
);
-- Create "CompletedDaily" table
CREATE TABLE `CompletedDaily` (
  `id` integer NULL,
  `user` integer NULL,
  `timestamp` integer NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `0` FOREIGN KEY (`user`) REFERENCES `Users` (`address`) ON UPDATE NO ACTION ON DELETE NO ACTION
);
-- Create "Quests" table
CREATE TABLE `Quests` (
  `id` varchar NULL,
  `quest_order` integer NULL,
  `reward_count` integer NULL,
  `day` integer NULL
);
-- Create index "Quests_id" to table: "Quests"
CREATE UNIQUE INDEX `Quests_id` ON `Quests` (`id`);
-- Create "CompletedQuests" table
CREATE TABLE `CompletedQuests` (
  `id` integer NULL,
  `user` integer NULL,
  `quest` integer NULL,
  `timestamp` integer NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `0` FOREIGN KEY (`quest`) REFERENCES `Quests` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT `1` FOREIGN KEY (`user`) REFERENCES `Users` (`address`) ON UPDATE NO ACTION ON DELETE NO ACTION
);
-- Create index "CompletedQuests_user_quest" to table: "CompletedQuests"
CREATE UNIQUE INDEX `CompletedQuests_user_quest` ON `CompletedQuests` (`user`, `quest`);
-- Create "Rewards" table
CREATE TABLE `Rewards` (
  `id` integer NULL,
  `token` varchar NULL,
  `price` integer NULL DEFAULT 0
);
-- Create index "Rewards_id" to table: "Rewards"
CREATE UNIQUE INDEX `Rewards_id` ON `Rewards` (`id`);
-- Create "CollectedRewards" table
CREATE TABLE `CollectedRewards` (
  `id` integer NULL,
  `user` integer NULL,
  `reward` integer NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `0` FOREIGN KEY (`reward`) REFERENCES `Rewards` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT `1` FOREIGN KEY (`user`) REFERENCES `Users` (`address`) ON UPDATE NO ACTION ON DELETE NO ACTION
);
-- Create index "CollectedRewards_user_reward" to table: "CollectedRewards"
CREATE UNIQUE INDEX `CollectedRewards_user_reward` ON `CollectedRewards` (`user`, `reward`);
-- Create "Coins" table
CREATE TABLE `Coins` (
  `id` integer NULL,
  `price` integer NULL DEFAULT 0
);
-- Create index "Coins_id" to table: "Coins"
CREATE UNIQUE INDEX `Coins_id` ON `Coins` (`id`);
-- Create "CollectedCoins" table
CREATE TABLE `CollectedCoins` (
  `id` integer NULL,
  `user` integer NULL,
  `coin` integer NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `0` FOREIGN KEY (`coin`) REFERENCES `Coins` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT `1` FOREIGN KEY (`user`) REFERENCES `Users` (`address`) ON UPDATE NO ACTION ON DELETE NO ACTION
);
-- Create index "CollectedCoins_user_coin" to table: "CollectedCoins"
CREATE UNIQUE INDEX `CollectedCoins_user_coin` ON `CollectedCoins` (`user`, `coin`);
-- Create "CollectedCoinsHistory" table
CREATE TABLE `CollectedCoinsHistory` (
  `id` integer NULL,
  `user` integer NULL,
  `coin` integer NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `0` FOREIGN KEY (`coin`) REFERENCES `Coins` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT `1` FOREIGN KEY (`user`) REFERENCES `Users` (`address`) ON UPDATE NO ACTION ON DELETE NO ACTION
);
-- Create index "CollectedCoinsHistory_user_coin" to table: "CollectedCoinsHistory"
CREATE UNIQUE INDEX `CollectedCoinsHistory_user_coin` ON `CollectedCoinsHistory` (`user`, `coin`);
-- Create "DailySettings" table
CREATE TABLE `DailySettings` (
  `id` varchar NULL,
  `value` integer NULL
);
-- Create index "DailySettings_id" to table: "DailySettings"
CREATE UNIQUE INDEX `DailySettings_id` ON `DailySettings` (`id`);
