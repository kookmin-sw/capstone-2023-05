
-- ************************************** Opinion

CREATE TABLE Opinion
(
 userId               uuid NOT NULL,
 battleId             uuid NOT NULL,
 roundNo              smallserial NOT NULL,
 "time"                 timestamp NOT NULL,
 noOfLikes            integer NOT NULL,
 maxOfLikesPerRefresh integer NOT NULL,
 content              varchar(50) NOT NULL,
 status               varchar(50) NOT NULL,
 CONSTRAINT PK_2 PRIMARY KEY ( userId, battleId, roundNo, "time" ),
 CONSTRAINT FK_2 FOREIGN KEY ( battleId, roundNo ) REFERENCES Round ( battleId, roundNo ),
 CONSTRAINT FK_3 FOREIGN KEY ( userId ) REFERENCES "User" ( userId )
);

CREATE INDEX FK_1 ON Opinion
(
 battleId,
 roundNo
);

CREATE INDEX FK_3 ON Opinion
(
 userId
);

-- ************************************** DiscussionBattle

CREATE TABLE DiscussionBattle
(
 battleId       uuid NOT NULL,
 ownerId        uuid NOT NULL,
 title          varchar(50) NOT NULL,
 status         status_enum NOT NULL,
 visibility     boolean NOT NULL,
 switchChance   boolean NOT NULL,
 startTime      timestamp NULL,
 endTime        timestamp NULL,
 description    varchar(50) NULL,
 maxNoOfPlayers integer NOT NULL,
 maxNoIfRounds  integer NOT NULL,
 maxNoVotes     integer NOT NULL,
 maxNoOfOpinion integer NOT NULL,
 refreshPeriod  integer NOT NULL,
 CONSTRAINT PK_1 PRIMARY KEY ( battleId ),
 CONSTRAINT FK_8 FOREIGN KEY ( ownerId ) REFERENCES "User" ( userId )
);

CREATE INDEX FK_2 ON DiscussionBattle
(
 ownerId
);


-- ************************************** Round

CREATE TABLE Round
(
 battleId    uuid NOT NULL,
 roundNo     smallserial NOT NULL,
 startTime   timestap NOT NULL,
 endTime     timestamp NULL,
 description varchar(50) NULL,
 CONSTRAINT PK_1 PRIMARY KEY ( battleId, roundNo ),
 CONSTRAINT FK_1 FOREIGN KEY ( battleId ) REFERENCES DiscussionBattle ( battleId )
);

CREATE INDEX FK_2 ON Round
(
 battleId
);


-- ************************************** Support

CREATE TABLE Support
(
 userId   uuid NOT NULL,
 battleId uuid NOT NULL,
 roundNo  smallserial NOT NULL,
 vote     uuid NOT NULL,
 "time"     timestamp NOT NULL,
 CONSTRAINT PK_2 PRIMARY KEY ( userId, battleId, roundNo ),
 CONSTRAINT FK_5 FOREIGN KEY ( userId ) REFERENCES "User" ( userId ),
 CONSTRAINT FK_6 FOREIGN KEY ( vote ) REFERENCES Team ( teamId ),
 CONSTRAINT FK_7 FOREIGN KEY ( battleId, roundNo ) REFERENCES Round ( battleId, roundNo )
);

CREATE INDEX FK_1 ON Support
(
 userId
);

CREATE INDEX FK_3 ON Support
(
 vote
);

CREATE INDEX FK_4 ON Support
(
 battleId,
 roundNo
);


-- ************************************** Team

CREATE TABLE Team
(
 teamId   uuid NOT NULL,
 battleId uuid NOT NULL,
 name     varchar(50) NOT NULL,
 image    bytea NOT NULL,
 CONSTRAINT PK_1 PRIMARY KEY ( teamId ),
 CONSTRAINT FK_4 FOREIGN KEY ( battleId ) REFERENCES DiscussionBattle ( battleId )
);

CREATE INDEX FK_2 ON Team
(
 battleId
);

-- ************************************** "User"

CREATE TABLE "User"
(
 userId   uuid NOT NULL,
 passwd   bytea NOT NULL,
 email    varchar(50) NOT NULL,
 nickname varchar(50) NOT NULL,
 profile  varchar(50) NULL,
 CONSTRAINT PK_1 PRIMARY KEY ( userId )
);



