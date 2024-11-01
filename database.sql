CREATE TABLE Users (
    address VARCHAR(150) UNIQUE PRIMARY KEY
);

CREATE TABLE CompletedDaily (
    id INTEGER PRIMARY KEY,
    user INTEGER REFERENCES Users(address),
    timestamp INTEGER
);

CREATE TABLE Quests (
    id VARCHAR(150) UNIQUE,
    quest_order INTEGER,
    reward_count INTEGER,
    day INTEGER
);

CREATE TABLE CompletedQuests (
    id INTEGER PRIMARY KEY,
    user INTEGER REFERENCES Users(address),
    quest INTEGER REFERENCES Quests(id),
    timestamp INTEGER,
    UNIQUE(user, quest)
);

CREATE TABLE Rewards (
    id INTEGER UNIQUE,
    blockchain_id INTEGER,
    collection VARCHAR(500),
    price INTEGER DEFAULT 0
);

CREATE TABLE CollectedRewards (
    id INTEGER PRIMARY KEY,
    transaction_hash VARCHAR(700),
    user INTEGER REFERENCES Users(address),
    reward INTEGER REFERENCES Rewards(id),
    reward_id INTEGER,
    UNIQUE(user, reward)
);

CREATE TABLE Coins (
    id INTEGER UNIQUE,
    price INTEGER DEFAULT 0
);

CREATE TABLE TodayCoins (
    id INTEGER PRIMARY KEY,
    user INTEGER REFERENCES Users(address),
    coin INTEGER REFERENCES Coins(id),
    is_collected BOOLEAN DEFAULT False,
    UNIQUE(user, coin)
);

CREATE TABLE ResetCoinsHistory (
    id INTEGER PRIMARY KEY,
    user INTEGER REFERENCES Users(address),
    timestamp INTEGER,
    collected_coins INTEGER,
    collected_coins_price INTEGER
);

CREATE TABLE Settings (
    id VARCHAR(100) UNIQUE,
    value INTEGER
);