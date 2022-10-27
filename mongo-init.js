db = db.getSiblingDB("app_store");

db.createCollection("users");
db.users.createIndex({ userId: 1 }, { unique: true });
db.models.createIndex({ modelId: 1, creatorUserId: 1 }, { unique: true });

db.users.insertMany([
  {
    userId: "master",
    name: "Master",
    password: "$2b$12$X86gHxJpDZEc4YHy2oLqU.pwNvvcJP16L5C292q39KuxXmCBW.xdG",
    adminPriv: true,
  },
  {
    userId: "dev1",
    name: "Developer One",
    password: "$2b$12$X86gHxJpDZEc4YHy2oLqU.pwNvvcJP16L5C292q39KuxXmCBW.xdG",
    adminPriv: false,
  },
]);
