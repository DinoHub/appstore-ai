db = db.getSiblingDB('app_store');

db.createCollection('users');
db.users.createIndex({userid: 'text'}, {unique:true})

db.users.insertMany([
 {
    userid: 'admin1',
    name: 'Tan Kee Chong',
    password: '$2b$12$X86gHxJpDZEc4YHy2oLqU.pwNvvcJP16L5C292q39KuxXmCBW.xdG',
    admin_priv: true
  },
  {
    userid: 'dev1',
    name: 'Developer One',
    password: '$2b$12$X86gHxJpDZEc4YHy2oLqU.pwNvvcJP16L5C292q39KuxXmCBW.xdG',
    admin_priv: false
  },

]);


