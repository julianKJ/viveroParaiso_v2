import { Router } from "express";
import prisma from "../prisma.js";
import { asyncHandler } from "../lib/http.js";

const router = Router();

router.get(
  "/resumen",
  asyncHandler(async (_req, res) => {
    const [productos, clientes, empleados, proveedores, recientes, stockBajo] = await Promise.all([
      prisma.producto.count(),
      prisma.cliente.count(),
      prisma.empleado.count(),
      prisma.proveedor.count(),
      prisma.producto.findMany({
        orderBy: { fechaRegistro: "desc" },
        take: 5,
        select: {
          id: true,
          nombre: true,
          categoria: true,
          cantidadDisponible: true,
          precioVenta: true,
          fechaRegistro: true,
        },
      }),
      prisma.producto.findMany({
        where: { cantidadDisponible: { lte: prisma.producto.fields.stockMinimo } },
        orderBy: { cantidadDisponible: "asc" },
        take: 8,
        select: {
          id: true,
          nombre: true,
          categoria: true,
          cantidadDisponible: true,
          stockMinimo: true,
        },
      }),
    ]);

    res.json({
      data: { productos, clientes, empleados, proveedores, recientes, stockBajo },
    });
  })
);

export default router;
