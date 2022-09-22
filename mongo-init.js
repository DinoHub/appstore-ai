db = db.getSiblingDB('app_store');

db.createCollection('users');

db.users.insertMany([
 {
    userid: 'sysadmin1',
    name: 'MasterAdmin1',
    password: '$2b$12$X86gHxJpDZEc4YHy2oLqU.pwNvvcJP16L5C292q39KuxXmCBW.xdG',
    admin_priv: true
  },
  {
    userid: 'developer1',
    name: 'TestDev1',
    password: '$2b$12$X86gHxJpDZEc4YHy2oLqU.pwNvvcJP16L5C292q39KuxXmCBW.xdG',
    admin_priv: true
  },

]);