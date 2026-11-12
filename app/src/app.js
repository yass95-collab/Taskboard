const express = require("express");

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

  return app;
}

module.exports = { createApp };