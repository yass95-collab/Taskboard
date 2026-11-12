const { createApp } = require("./app");
const db = require("./db");

const port = Number(process.env.APP_PORT);
if (!port) {
  throw new Error("Variable d'environnement manquante : APP_PORT");
}

const app = createApp(db);

const server = app.listen(port, () => {
  console.log(`TaskBoard écoute sur le port ${port}`);
});

process.on("SIGTERM", () => {
  server.close(() => {
    db.pool.end().then(() => process.exit(0));
  });
});