CREATE TYPE "battle_status" AS ENUM ('BEFORE_OPEN', 'RUNNING', 'CLOSED');
CREATE TYPE "opinion_status" AS ENUM ('CANDIDATE', 'PUBLISHED', 'DROPPED', 'REPORTED');

CREATE TABLE "User" (
  "userId" varchar(50) NOT NULL,
  "passwd" bytea NOT NULL,
  "nickname" varchar(50) NOT NULL,
  "profile" varchar(50) NULL,
  CONSTRAINT PK_USER_ID PRIMARY KEY ("userId")
);
CREATE TABLE "DiscussionBattle" (
  "battleId" varchar(6) NOT NULL,
  "ownerId" varchar(50) NOT NULL,
  "title" varchar(50) NOT NULL,
  "status" battle_status NOT NULL,
  "startTime" timestamp NULL,
  "endTime" timestamp NULL,
  "description" varchar(100) NULL,
  "refreshPeriod"  integer NOT NULL,
  "maxNoOfRefresh" integer NOT NULL,
  "maxNoOfRounds" integer NOT NULL,
  "maxNoOfVotes" integer NOT NULL,
  "maxNoOfOpinion" integer NOT NULL,
  CONSTRAINT PK_DISCUSSION_BATTLE_ID PRIMARY KEY ("battleId"),
  CONSTRAINT FK_8 FOREIGN KEY ("ownerId") REFERENCES "User" ("userId")
);
CREATE TABLE "Round" (
  "battleId" VARCHAR(6) NOT NULL,
  "roundNo" serial NOT NULL,
  "startTime" timestamp NULL,
  "endTime" timestamp NULL,
  "description" varchar(100) NULL,
  CONSTRAINT PK_ROUND_ID PRIMARY KEY ("battleId", "roundNo"),
  CONSTRAINT FK_1 FOREIGN KEY ("battleId") REFERENCES "DiscussionBattle" ("battleId")
);
CREATE TABLE "Opinion" (
  "userId" varchar(50) NOT NULL,
  "battleId" varchar(6) NOT NULL,
  "roundNo" serial NOT NULL,
  "order" serial NOT NULL,
  "noOfLikes" integer NOT NULL,
  "content" varchar(150) NOT NULL,
  "timestamp" timestamp NOT NULL,
  "publishTime" timestamp NULL,
  "dropTime" timestamp NULL,
  "status" opinion_status NOT NULL,
  CONSTRAINT PK_OPINION_ID PRIMARY KEY ("userId", "battleId", "roundNo", "order"),
  CONSTRAINT FK_2 FOREIGN KEY ("battleId", "roundNo") REFERENCES "Round" ("battleId", "roundNo"),
  CONSTRAINT FK_3 FOREIGN KEY ("userId") REFERENCES "User" ("userId")
);
CREATE TABLE "Team" (
  "teamId" serial NOT NULL,
  "battleId" varchar(6) NOT NULL,
  "name" varchar(50) NOT NULL,
  "image" bytea NOT NULL,
  CONSTRAINT PK_TEAM_ID PRIMARY KEY ("teamId"),
  CONSTRAINT FK_4 FOREIGN KEY ("battleId") REFERENCES "DiscussionBattle" ("battleId")
);
CREATE TABLE "Support" (
  "userId" varchar(50) NOT NULL,
  "battleId" varchar(6) NOT NULL,
  "roundNo" serial NOT NULL,
  "vote" serial NOT NULL,
  "time" timestamp NOT NULL,
  CONSTRAINT PK_SUPPORT_ID PRIMARY KEY ("userId", "battleId", "roundNo"),
  CONSTRAINT FK_5 FOREIGN KEY ("userId") REFERENCES "User" ("userId"),
  CONSTRAINT FK_6 FOREIGN KEY ("vote") REFERENCES "Team" ("teamId"),
  CONSTRAINT FK_7 FOREIGN KEY ("battleId", "roundNo") REFERENCES "Round" ("battleId", "roundNo")
);

-- Local Testing Dummy Data
INSERT INTO "User" ("userId", "passwd", "nickname", profile)
VALUES 
    ('joon@kookmin.ac.kr', E'\\x6a6f6f6e313233', 'lyj', 'www.example.com/joon/profile'),
    ('hoon@kookmin.ac.kr', E'\\x686f6f6e313233', 'sch', 'www.example.com/hoon/profile'),
    ('gyun@kookmin.ac.kr', E'\\x6779756e313233', 'lyg', 'www.example.com/gyun/profile'),
    ('ho@kookmin.ac.kr', E'\\x686f313233', 'lsh', 'www.example.com/ho/profile'),
    ('wuk@kookmin.ac.kr', E'\\x77756b313233', 'ljw', 'www.example.com/ljw/profile');

INSERT INTO "DiscussionBattle" ("battleId", "ownerId", "title", "status", "startTime", "endTime", "description", "refreshPeriod", "maxNoOfRefresh", "maxNoOfRounds", "maxNoOfVotes", "maxNoOfOpinion")
VALUES 
    ('ABC123', 'joon@kookmin.ac.kr', 'Which is many? door or wheel', 'BEFORE_OPEN', '2023-05-01 12:00:00', '2023-05-31 12:00:00', 'Our first battle', 300, 10, 3, 10, 50);

INSERT INTO "Round" ("battleId", "startTime", "endTime", "description")
VALUES 
    ('ABC123', '2023-05-01 12:00:00', '2023-05-07 12:00:00', 'Initial round'),
    ('ABC123', '2023-05-08 12:00:00', '2023-05-14 12:00:00', 'Second round'),
    ('ABC123', '2023-05-15 12:00:00', '2023-05-21 12:00:00', 'Final round');

INSERT INTO "Team" ("battleId", "name", "image")
VALUES
    ('ABC123', 'Team Door', '0123456789ABCDEF'),
    ('ABC123', 'Team Wheel', 'FEDCBA9876543210');