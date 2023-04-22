CREATE TYPE "battle_status" AS ENUM ('BEFORE_OPEN', 'RUNNING', 'CLOSED');
CREATE TYPE "opinion_status" AS ENUM ('CANDIDATE', 'PUBLISHED', 'DROPPED', 'REPORTED');
CREATE TABLE "User" (
  userId varchar(50) NOT NULL,
  passwd bytea NOT NULL,
  nickname varchar(50) NOT NULL,
  profile varchar(50) NULL,
  CONSTRAINT PK_USER_ID PRIMARY KEY (userId)
);
CREATE TABLE DiscussionBattle (
  battleId varchar(6) NOT NULL,
  ownerId varchar(50) NOT NULL,
  title varchar(50) NOT NULL,
  status battle_status NOT NULL,
  visibility boolean NOT NULL,
  switchChance boolean NOT NULL,
  startTime timestamp NULL,
  endTime timestamp NULL,
  description varchar(100) NULL,
  maxNoIfRounds integer NOT NULL,
  maxNoVotes integer NOT NULL,
  maxNoOfOpinion integer NOT NULL,
  CONSTRAINT PK_DISCUSSION_BATTLE_ID PRIMARY KEY (battleId),
  CONSTRAINT FK_8 FOREIGN KEY (ownerId) REFERENCES "User" (userId)
);
CREATE TABLE Round (
  battleId VARCHAR(6) NOT NULL,
  roundNo serial NOT NULL,
  startTime timestamp NOT NULL,
  endTime timestamp NULL,
  description varchar(100) NULL,
  CONSTRAINT PK_ROUND_ID PRIMARY KEY (battleId, roundNo),
  CONSTRAINT FK_1 FOREIGN KEY (battleId) REFERENCES DiscussionBattle (battleId)
);
CREATE TABLE Opinion (
  userId varchar(50) NOT NULL,
  battleId varchar(6) NOT NULL,
  roundNo serial NOT NULL,
  "time" timestamp NOT NULL,
  noOfLikes integer NOT NULL,
  content varchar(150) NOT NULL,
  status opinion_status NOT NULL,
  CONSTRAINT PK_OPINION_ID PRIMARY KEY (userId, battleId, roundNo, "time"),
  CONSTRAINT FK_2 FOREIGN KEY (battleId, roundNo) REFERENCES Round (battleId, roundNo),
  CONSTRAINT FK_3 FOREIGN KEY (userId) REFERENCES "User" (userId)
);
CREATE TABLE Team (
  teamId serial NOT NULL,
  battleId varchar(6) NOT NULL,
  name varchar(50) NOT NULL,
  image bytea NOT NULL,
  CONSTRAINT PK_TEAM_ID PRIMARY KEY (teamId),
  CONSTRAINT FK_4 FOREIGN KEY (battleId) REFERENCES DiscussionBattle (battleId)
);
CREATE TABLE Support (
  userId varchar(50) NOT NULL,
  battleId varchar(6) NOT NULL,
  roundNo serial NOT NULL,
  vote serial NOT NULL,
  "time" timestamp NOT NULL,
  CONSTRAINT PK_SUPPORT_ID PRIMARY KEY (userId, battleId, roundNo),
  CONSTRAINT FK_5 FOREIGN KEY (userId) REFERENCES "User" (userId),
  CONSTRAINT FK_6 FOREIGN KEY (vote) REFERENCES Team (teamId),
  CONSTRAINT FK_7 FOREIGN KEY (battleId, roundNo) REFERENCES Round (battleId, roundNo)
);