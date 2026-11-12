const express = require("express");

const COLUMNS = "id, title, completed, created_at";

function parseId(value) {
  const id = Number(value);
  return Number.isInteger(id) && id > 0 ? id : null;
}

function isValidTitle(title) {
  return typeof title === "string" && title.trim().length > 0 && title.trim().length <= 255;
}

function createTasksRouter(db) {
  const router = express.Router();

  router.get("/", async (req, res) => {
    const result = await db.pool.query(
      `SELECT ${COLUMNS} FROM tasks ORDER BY created_at DESC, id DESC`
    );
    res.json(result.rows);
  });

  router.get("/:id", async (req, res) => {
    const id = parseId(req.params.id);
    if (!id) return res.status(400).json({ error: "Identifiant invalide" });

    const result = await db.pool.query(`SELECT ${COLUMNS} FROM tasks WHERE id = $1`, [id]);
    if (result.rowCount === 0) return res.status(404).json({ error: "Tâche introuvable" });

    res.json(result.rows[0]);
  });

  router.post("/", async (req, res) => {
    const { title } = req.body ?? {};
    if (!isValidTitle(title)) {
      return res.status(400).json({ error: "Le titre est obligatoire (255 caractères maximum)" });
    }

    const result = await db.pool.query(
      `INSERT INTO tasks (title) VALUES ($1) RETURNING ${COLUMNS}`,
      [title.trim()]
    );
    res.status(201).json(result.rows[0]);
  });

  router.patch("/:id", async (req, res) => {
    const id = parseId(req.params.id);
    if (!id) return res.status(400).json({ error: "Identifiant invalide" });

    const { title, completed } = req.body ?? {};
    if (title === undefined && completed === undefined) {
      return res.status(400).json({ error: "Rien à modifier" });
    }
    if (title !== undefined && !isValidTitle(title)) {
      return res.status(400).json({ error: "Le titre est obligatoire (255 caractères maximum)" });
    }
    if (completed !== undefined && typeof completed !== "boolean") {
      return res.status(400).json({ error: "completed doit valoir true ou false" });
    }

    const result = await db.pool.query(
      `UPDATE tasks
       SET title = COALESCE($1, title), completed = COALESCE($2, completed)
       WHERE id = $3
       RETURNING ${COLUMNS}`,
      [title === undefined ? null : title.trim(), completed === undefined ? null : completed, id]
    );
    if (result.rowCount === 0) return res.status(404).json({ error: "Tâche introuvable" });

    res.json(result.rows[0]);
  });

  router.delete("/:id", async (req, res) => {
    const id = parseId(req.params.id);
    if (!id) return res.status(400).json({ error: "Identifiant invalide" });

    const result = await db.pool.query("DELETE FROM tasks WHERE id = $1", [id]);
    if (result.rowCount === 0) return res.status(404).json({ error: "Tâche introuvable" });

    res.status(204).end();
  });

  return router;
}

module.exports = { createTasksRouter };