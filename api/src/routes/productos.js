import { Router } from "express";
import prisma from "../prisma.js";
import {
  HttpError,
  aDecimal,
  aEntero,
  asyncHandler,
  idNumerico,
  paginacion,
  requeridos,
  respuestaPaginada,
  textoOpcional,
} from "../lib/http.js";

const router = Router();

const CAMPOS_OBLIGATORIOS = [
  "nombre",
  "categoria",
  "precio_compra",
  "precio_venta",
  "cantidad_disponible",
  "stock_minimo",
  "proveedor_id",
];

const INCLUIR_PROVEEDOR = { proveedor: { select: { id: true, nombreEmpresa: true } } };

function normalizar(body = {}) {
  requeridos(CAMPOS_OBLIGATORIOS, body);
  return {
    nombre: String(body.nombre).trim(),
    categoria: String(body.categoria).trim(),
    descripcion: textoOpcional(body.descripcion),
    precioCompra: aDecimal(body.precio_compra, "precio_compra"),
    precioVenta: aDecimal(body.precio_venta, "precio_venta"),
    cantidadDisponible: aEntero(body.cantidad_disponible, "cantidad_disponible"),
    stockMinimo: aEntero(body.stock_minimo, "stock_minimo"),
    proveedorId: idNumerico(body.proveedor_id, "proveedor_id"),
  };
}

function filtro(query = {}) {
  const where = {};
  if (query.q) {
    const termino = String(query.q).trim();
    where.OR = [
      { nombre: { contains: termino } },
      { categoria: { contains: termino } },
      { descripcion: { contains: termino } },
    ];
  }
  if (query.categoria) {
    where.categoria = String(query.categoria).trim();
  }
  if (query.bajo_stock === "true" || query.bajo_stock === "1") {
    where.cantidadDisponible = { lte: prisma.producto.fields.stockMinimo };
  }
  return where;
}

router.get(
  "/",
  asyncHandler(async (req, res) => {
    const pag = paginacion(req.query, 10);
    const where = filtro(req.query);
    const [data, total] = await Promise.all([
      prisma.producto.findMany({
        where,
        include: INCLUIR_PROVEEDOR,
        orderBy: { fechaRegistro: "desc" },
        skip: pag.skip,
        take: pag.limite,
      }),
      prisma.producto.count({ where }),
    ]);
    res.json(respuestaPaginada(data, total, pag));
  })
);

router.get(
  "/categorias",
  asyncHandler(async (_req, res) => {
    const filas = await prisma.producto.findMany({
      distinct: ["categoria"],
      select: { categoria: true },
      orderBy: { categoria: "asc" },
    });
    res.json({ data: filas.map((fila) => fila.categoria) });
  })
);

router.get(
  "/:id",
  asyncHandler(async (req, res) => {
    const producto = await prisma.producto.findUnique({
      where: { id: idNumerico(req.params.id) },
      include: INCLUIR_PROVEEDOR,
    });
    if (!producto) throw new HttpError(404, "Producto no encontrado.");
    res.json({ data: producto });
  })
);

router.post(
  "/",
  asyncHandler(async (req, res) => {
    const producto = await prisma.producto.create({
      data: normalizar(req.body),
      include: INCLUIR_PROVEEDOR,
    });
    res.status(201).json({ data: producto });
  })
);

router.put(
  "/:id",
  asyncHandler(async (req, res) => {
    const producto = await prisma.producto.update({
      where: { id: idNumerico(req.params.id) },
      data: normalizar(req.body),
      include: INCLUIR_PROVEEDOR,
    });
    res.json({ data: producto });
  })
);

router.delete(
  "/:id",
  asyncHandler(async (req, res) => {
    const id = idNumerico(req.params.id);
    const existe = await prisma.producto.findUnique({ where: { id }, select: { id: true } });
    if (!existe) throw new HttpError(404, "Producto no encontrado.");
    await prisma.producto.delete({ where: { id } });
    res.json({ data: { id, eliminado: true } });
  })
);

export default router;
