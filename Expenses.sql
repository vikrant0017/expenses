CREATE TABLE "expenses" (
  "id" integer PRIMARY KEY,
  "group_id" integer NOT NULL,
  "user_id" integer NOT NULL,
  "title" varchar NOT NULL,
  "description" varchar,
  "amount" numeric(10,2) NOT NULL,
  "timestamp" timestamp NOT NULL,
  "created_at" timestamp NOT NULL,
  "updated_at" timestamp NOT NULL
);

CREATE TABLE "splits" (
  "id" integer PRIMARY KEY,
  "group_id" integer NOT NULL,
  "expense_id" integer NOT NULL,
  "user_id" integer NOT NULL,
  "amount" numeric(10,2) NOT NULL
);

CREATE TABLE "users" (
  "id" integer PRIMARY KEY,
  "name" varchar NOT NULL
);

CREATE TABLE "groups" (
  "id" integer PRIMARY KEY,
  "name" varchar NOT NULL
);

CREATE TABLE "user_group" (
  "user_id" integer,
  "group_id" integer,
  PRIMARY KEY ("user_id", "group_id")
);

COMMENT ON COLUMN "splits"."user_id" IS 'This is the user who is part of the share and differ from user_id in expense';

COMMENT ON COLUMN "splits"."amout" IS 'Share of the user';

ALTER TABLE "expenses" ADD FOREIGN KEY ("group_id") REFERENCES "groups" ("id");

ALTER TABLE "expenses" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "splits" ADD FOREIGN KEY ("group_id") REFERENCES "groups" ("id");

ALTER TABLE "splits" ADD FOREIGN KEY ("expense_id") REFERENCES "expenses" ("id");

ALTER TABLE "splits" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "user_group" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "user_group" ADD FOREIGN KEY ("group_id") REFERENCES "groups" ("id");
