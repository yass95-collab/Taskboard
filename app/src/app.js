const express = require("express");
const path = require("path");
const { createTasksRouter } = require("./tasks");

function createApp(db) {
  const app = express();
  app.use(express.json());

  app.get("/healthz", (req, res) => {
    res.status(200).json({ status: "ok" });
  });

  app.get("/readyz", async (req, res) => {
    try {
      await db.checkConnection();
      res.status(200).json({ status: "ready" });
    } catch {
      res.status(503).json({ status: "unavailable" });
    }
  });
  app.use(express.static(path.join(__dirname, "..", "public")));
  app.use("/api/tasks", createTasksRouter(db));

  app.use((err, req, res, next) => {
    if (err.type === "entity.parse.failed") {
      return res.status(400).json({ error: "JSON invalide" });
    }
    console.error(err);
    res.status(500).json({ error: "Erreur interne du serveur" });
  });

  return app;
}

module.exports = { createApp };