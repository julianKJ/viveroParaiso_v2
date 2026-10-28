import { Router } from "express";
import prisma from "../prisma.js";
import {
  HttpError,
  asyncHandler,
  enumValido,
  idNumerico,
  paginacion,
  requeridos,
  respuestaPaginada,
  textoOpcional,
} from "../lib/http.js";

const router = Router();

const ESTADOS = ["Activo", "Inactivo"];
const CAMPOS_OBLIGATORIOS = [
  "nombre_empresa",
  "nit",
  "persona_contacto",
  "telefono",
  "correo",
  "direccion",
  "estado",
];

function normalizar(body = {}) {
  requeridos(CAMPOS_OBLIGATORIOS, body);
  return {
    nombreEmpresa: String(body.nombre_empresa).trim(),
    nit: String(body.nit).trim(),
    personaContacto: String(body.persona_contacto).trim(),
    telefono: String(body.telefono).trim(),
    correo: String(body.correo).trim(),
    direccion: String(body.direccion).trim(),
    productosSuministrados: textoOpcional(body.productos_suministrados),
    estado: enumValido(String(body.estado).trim(), ESTADOS, "estado"),
  };
}

router.get(
  "/",
  asyncHandler(async (req, res) => {
    const pag = paginacion(req.query, 10);
    const where = {};
    if (req.query.q) {
      const termino = String(req.query.q).trim();
      where.OR = [
        { nombreEmpresa: { contains: termino } },
        { nit: { contains: termino } },
        { personaContacto: { contains: termino } },
        { correo: { contains: termino } },
      ];
    }
    if (req.query.estado) {
      where.estado = enumValido(String(req.query.estado).trim(), ESTADOS, "estado");
    }
    const [data, total] = await Promise.all([
      prisma.proveedor.findMany({
        where,
        orderBy: { nombreEmpresa: "asc" },
        skip: pag.skip,
        take: pag.limite,
      }),
      prisma.proveedor.count({ where }),
    ]);
    res.json(respuestaPaginada(data, total, pag));
  })
);

router.get(
  "/activos",
  asyncHandler(async (_req, res) => {
    const data = await prisma.proveedor.findMany({
      where: { estado: "Activo" },
      select: { id: true, nombreEmpresa: true },
      orderBy: { nombreEmpresa: "asc" },
    });
    res.json({ data });
  })
);

router.get(
  "/:id",
  asyncHandler(async (req, res) => {
    const id = idNumerico(req.params.id);
    const proveedor = await prisma.proveedor.findUnique({
      where: { id },
      include: { _count: { select: { productos: true } } },
    });
    if (!proveedor) throw new HttpError(404, "Proveedor no encontrado.");
    const { _count, ...resto } = proveedor;
    res.json({ data: { ...resto, productosAsociados: _count.productos } });
  })
);

router.post(
  "/",
  asyncHandler(async (req, res) => {
    const proveedor = await prisma.proveedor.create({ data: normalizar(req.body) });
    res.status(201).json({ data: proveedor });
  })
);

router.put(
  "/:id",
  asyncHandler(async (req, res) => {
    const proveedor = await prisma.proveedor.update({
      where: { id: idNumerico(req.params.id) },
      data: normalizar(req.body),
    });
    res.json({ data: proveedor });
  })
);

router.delete(
  "/:id",
  asyncHandler(async (req, res) => {
    const id = idNumerico(req.params.id);
    const proveedor = await prisma.proveedor.findUnique({
      where: { id },
      select: { id: true, _count: { select: { productos: true } } },
    });
    if (!proveedor) throw new HttpError(404, "Proveedor no encontrado.");
    if (proveedor._count.productos > 0) {
      throw new HttpError(
        409,
        `No se puede eliminar: el proveedor tiene ${proveedor._count.productos} producto(s) asociado(s).`
      );
    }
    await prisma.proveedor.delete({ where: { id } });
    res.json({ data: { id, eliminado: true } });
  })
);

export default router;
