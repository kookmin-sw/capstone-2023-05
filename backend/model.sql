CREATE TYPE "status_enum" AS ENUM (
  'Not yet',
  'Running',
  'Finished'
);

CREATE TABLE "Opinion" (
  "opinion_id" uuid PRIMARY KEY NOT NULL,
  "player_id" uuid NOT NULL,
  "team_id" uuid NOT NULL,
  "voted_count" integer NOT NULL,
  "round" integer NOT NULL,
  "content" text NOT NULL,
  "timestamp" timestamp NOT NULL
);

CREATE TABLE "Player" (
  "player_id" uuid PRIMARY KEY NOT NULL,
  "team_id" uuid NOT NULL,
  "connect_id" varchar(50) NOT NULL
);

CREATE TABLE "Room" (
  "room_id" uuid PRIMARY KEY NOT NULL,
  "current_round" integer NOT NULL,
  "status" status_enum NOT NULL
);

CREATE TABLE "RoomConfig" (
  "config_id" varchar(50) PRIMARY KEY NOT NULL,
  "owner_id" uuid NOT NULL,
  "room_id" uuid NOT NULL,
  "title" text NOT NULL,
  "visibility" boolean NOT NULL,
  "switch_chance" boolean NOT NULL,
  "max_player_count" integer NOT NULL,
  "end_round" integer NOT NULL,
  "round_end_time" time NOT NULL,
  "votes_per_user" integer NOT NULL,
  "opinion_per_user" integer NOT NULL
);

CREATE TABLE "Team" (
  "team_id" uuid PRIMARY KEY NOT NULL,
  "room_id" uuid NOT NULL,
  "image" bytea NOT NULL,
  "name" varchar(50) NOT NULL
);

CREATE TABLE "User" (
  "user_id" uuid PRIMARY KEY NOT NULL,
  "email" varchar(320) NOT NULL,
  "nickname" varchar(50) NOT NULL,
  "profile" varchar(50) NOT NULL,
  "password" varchar(50) NOT NULL
);

ALTER TABLE "Opinion" ADD CONSTRAINT "FK_1" FOREIGN KEY ("player_id") REFERENCES "Player" ("player_id");

ALTER TABLE "Opinion" ADD CONSTRAINT "FK_7" FOREIGN KEY ("team_id") REFERENCES "Team" ("team_id");

ALTER TABLE "Player" ADD CONSTRAINT "FK_2" FOREIGN KEY ("player_id") REFERENCES "User" ("user_id");

ALTER TABLE "Player" ADD CONSTRAINT "FK_3" FOREIGN KEY ("team_id") REFERENCES "Team" ("team_id");

ALTER TABLE "RoomConfig" ADD CONSTRAINT "FK_4" FOREIGN KEY ("owner_id") REFERENCES "User" ("user_id");

ALTER TABLE "RoomConfig" ADD CONSTRAINT "FK_5" FOREIGN KEY ("room_id") REFERENCES "Room" ("room_id");

ALTER TABLE "Team" ADD CONSTRAINT "FK_6" FOREIGN KEY ("room_id") REFERENCES "Room" ("room_id");
