db = db.getSiblingDB('admin');  // Переключаемся на админскую БД

db.createUser({
  user: "root",
  pwd: "example",
  roles: [
    { role: "readWrite", db: "file_metadata" },
    { role: "dbAdmin", db: "file_metadata" }
  ]
});

db = db.getSiblingDB('file_metadata');  // Переключаемся на нужную БД

db.createCollection('files');

db.files.createIndex({ filename: 1 }, { unique: true });

db.files.insertMany([
  { filename: "example1.txt", metadata: "Sample file 1" },
  { filename: "example2.txt", metadata: "Sample file 2" }
]);
