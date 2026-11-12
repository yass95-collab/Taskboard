// src/db.js : connexion à la base PostgreSQL
const { Pool } = require("pg");

// Lit une variable d'environnement obligatoire, et arrête l'appli si elle manque
function requireEnv(name) {
  const value = process.env[name];
  if (value === undefined || value === "") {
    throw new Error(`Variable d'environnement manquante : ${name}`);
  }
  return value;
}

// Pool = ensemble de connexions réutilisées par toutes les requêtes
const pool = new Pool({
  host: requireEnv("DB_HOST"),
  port: Number(requireEnv("DB_PORT")),
  database: requireEnv("DB_NAME"),
  user: requireEnv("DB_USER"),
  password: requireEnv("DB_PASSWORD"),
  connectionTimeoutMillis: 2000, // abandonne après 2 s si la base ne répond pas
});

// Sans ce gestionnaire, une coupure de la base ferait planter toute l'appli
pool.on("error", (err) => {
  console.error("Erreur sur la connexion PostgreSQL :", err.message);
});

// Vérifie que la base répond (utilisé par /readyz)
async function checkConnection() {
  await pool.query("SELECT 1");
}

module.exports = { pool, checkConnection };