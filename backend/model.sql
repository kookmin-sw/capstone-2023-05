CREATE TYPE "status_enum" AS ENUM ('BEFORE_OPEN', 'RUNNING', 'CLOSED');
CREATE TABLE "User" (
  userId uuid NOT NULL,
  passwd bytea NOT NULL,
  email varchar(50) NOT NULL,
  nickname varchar(50) NOT NULL,
  profile varchar(50) NULL,
  CONSTRAINT PK_USER_ID PRIMARY KEY (userId)
);
CREATE TABLE DiscussionBattle (
  battleId uuid NOT NULL,
  ownerId uuid NOT NULL,
  title varchar(50) NOT NULL,
  status status_enum NOT NULL,
  visibility boolean NOT NULL,
  switchChance boolean NOT NULL,
  startTime timestamp NULL,
  endTime timestamp NULL,
  description varchar(50) NULL,
  maxNoOfPlayers integer NOT NULL,
  maxNoIfRounds integer NOT NULL,
  maxNoVotes integer NOT NULL,
  maxNoOfOpinion integer NOT NULL,
  CONSTRAINT PK_DISCUSSION_BATTLE_ID PRIMARY KEY (battleId),
  CONSTRAINT FK_8 FOREIGN KEY (ownerId) REFERENCES "User" (userId)
);
CREATE TABLE Round (
  battleId uuid NOT NULL,
  roundNo smallserial NOT NULL,
  startTime timestamp NOT NULL,
  endTime timestamp NULL,
  description varchar(50) NULL,
  CONSTRAINT PK_ROUND_ID PRIMARY KEY (battleId, roundNo),
  CONSTRAINT FK_1 FOREIGN KEY (battleId) REFERENCES DiscussionBattle (battleId)
);
CREATE TABLE Opinion (
  userId uuid NOT NULL,
  battleId uuid NOT NULL,
  roundNo smallserial NOT NULL,
  "time" timestamp NOT NULL,
  noOfLikes integer NOT NULL,
  content varchar(50) NOT NULL,
  status varchar(50) NOT NULL,
  CONSTRAINT PK_OPINION_ID PRIMARY KEY (userId, battleId, roundNo, "time"),
  CONSTRAINT FK_2 FOREIGN KEY (battleId, roundNo) REFERENCES Round (battleId, roundNo),
  CONSTRAINT FK_3 FOREIGN KEY (userId) REFERENCES "User" (userId)
);
CREATE TABLE Team (
  teamId uuid NOT NULL,
  battleId uuid NOT NULL,
  name varchar(50) NOT NULL,
  image bytea NOT NULL,
  CONSTRAINT PK_TEAM_ID PRIMARY KEY (teamId),
  CONSTRAINT FK_4 FOREIGN KEY (battleId) REFERENCES DiscussionBattle (battleId)
);
CREATE TABLE Support (
  userId uuid NOT NULL,
  battleId uuid NOT NULL,
  roundNo smallserial NOT NULL,
  vote uuid NOT NULL,
  "time" timestamp NOT NULL,
  CONSTRAINT PK_SUPPORT_ID PRIMARY KEY (userId, battleId, roundNo),
  CONSTRAINT FK_5 FOREIGN KEY (userId) REFERENCES "User" (userId),
  CONSTRAINT FK_6 FOREIGN KEY (vote) REFERENCES Team (teamId),
  CONSTRAINT FK_7 FOREIGN KEY (battleId, roundNo) REFERENCES Round (battleId, roundNo)
);