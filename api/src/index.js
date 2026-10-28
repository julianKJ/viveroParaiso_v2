import "dotenv/config";
import express from "express";
import cors from "cors";

import prisma from "./prisma.js";
import { HttpError, asyncHandler } from "./lib/http.js";
import productosRoutes from "./routes/productos.js";
import clientesRoutes from "./routes/clientes.js";
import empleadosRoutes from "./routes/empleados.js";
import proveedoresRoutes from "./routes/proveedores.js";
import dashboardRoutes from "./routes/dashboard.js";

const app = express();
const puerto = Number(process.env.PORT) || 4000;
const origenes = (process.env.CORS_ORIGIN || "http://127.0.0.1:5000")
  .split(",")
  .map((origen) => origen.trim());

app.use(cors({ origin: origenes }));
app.use(express.json({ limit: "1mb" }));

app.get(
  "/api/health",
  asyncHandler(async (_req, res) => {
    await prisma.$queryRaw`SELECT 1`;
    res.json({ ok: true, base: "vivero_paraiso", momento: new Date().toISOString() });
  })
);

app.use("/api/productos", productosRoutes);
app.use("/api/clientes", clientesRoutes);
app.use("/api/empleados", empleadosRoutes);
app.use("/api/proveedores", proveedoresRoutes);
app.use("/api/dashboard", dashboardRoutes);

app.use((_req, res) => {
  res.status(404).json({ error: "Ruta no encontrada." });
});

// Middleware central de errores: traduce errores de Prisma a respuestas HTTP claras.
app.use((error, _req, res, _next) => {
  if (error instanceof HttpError) {
    return res.status(error.status).json({ error: error.message, detalles: error.detalles });
  }
  if (error?.code === "P2002") {
    return res.status(409).json({
      error: "Ya existe un registro con ese valor único.",
      detalles: error.meta?.target ?? null,
    });
  }
  if (error?.code === "P2003") {
    return res.status(409).json({
      error: "La operación viola una referencia: hay registros relacionados (por ejemplo, un proveedor con productos).",
    });
  }
  if (error?.code === "P2025") {
    return res.status(404).json({ error: "El registro no existe." });
  }
  console.error("[API] Error no controlado:", error);
  return res.status(500).json({ error: "Error interno del servidor." });
});

const servidor = app.listen(puerto, () => {
  console.log(`API Vivero El Paraíso escuchando en http://127.0.0.1:${puerto}/api`);
});

async function apagar(senal) {
  console.log(`\n[API] ${senal} recibido. Cerrando conexiones...`);
  servidor.close();
  await prisma.$disconnect();
  process.exit(0);
}

process.on("SIGINT", () => apagar("SIGINT"));
process.on("SIGTERM", () => apagar("SIGTERM"));
