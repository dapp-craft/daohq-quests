-- Disable the enforcement of foreign-keys constraints
PRAGMA foreign_keys = off;
-- Drop "DailySettings" table
DROP TABLE `DailySettings`;
-- Create "Settings" table
CREATE TABLE `Settings` (
  `id` varchar NULL,
  `value` integer NULL
);
-- Create index "Settings_id" to table: "Settings"
CREATE UNIQUE INDEX `Settings_id` ON `Settings` (`id`);
-- Enable back the enforcement of foreign-keys constraints
PRAGMA foreign_keys = on;
