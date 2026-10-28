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
} from "../lib/http.js";

const router = Router();

const TIPOS_DOCUMENTO = ["CC", "CE", "NIT", "Pasaporte", "TI"];
const CAMPOS_OBLIGATORIOS = [
  "nombres",
  "apellidos",
  "tipo_documento",
  "numero_documento",
  "telefono",
  "correo",
  "direccion",
];

function normalizar(body = {}) {
  requeridos(CAMPOS_OBLIGATORIOS, body);
  return {
    nombres: String(body.nombres).trim(),
    apellidos: String(body.apellidos).trim(),
    tipoDocumento: enumValido(String(body.tipo_documento).trim(), TIPOS_DOCUMENTO, "tipo_documento"),
    numeroDocumento: String(body.numero_documento).trim(),
    telefono: String(body.telefono).trim(),
    correo: String(body.correo).trim(),
    direccion: String(body.direccion).trim(),
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
        { nombres: { contains: termino } },
        { apellidos: { contains: termino } },
        { numeroDocumento: { contains: termino } },
        { correo: { contains: termino } },
      ];
    }
    const [data, total] = await Promise.all([
      prisma.cliente.findMany({
        where,
        orderBy: [{ apellidos: "asc" }, { nombres: "asc" }],
        skip: pag.skip,
        take: pag.limite,
      }),
      prisma.cliente.count({ where }),
    ]);
    res.json(respuestaPaginada(data, total, pag));
  })
);

router.get(
  "/:id",
  asyncHandler(async (req, res) => {
    const cliente = await prisma.cliente.findUnique({ where: { id: idNumerico(req.params.id) } });
    if (!cliente) throw new HttpError(404, "Cliente no encontrado.");
    res.json({ data: cliente });
  })
);

router.post(
  "/",
  asyncHandler(async (req, res) => {
    const cliente = await prisma.cliente.create({ data: normalizar(req.body) });
    res.status(201).json({ data: cliente });
  })
);

router.put(
  "/:id",
  asyncHandler(async (req, res) => {
    const cliente = await prisma.cliente.update({
      where: { id: idNumerico(req.params.id) },
      data: normalizar(req.body),
    });
    res.json({ data: cliente });
  })
);

router.delete(
  "/:id",
  asyncHandler(async (req, res) => {
    const id = idNumerico(req.params.id);
    const existe = await prisma.cliente.findUnique({ where: { id }, select: { id: true } });
    if (!existe) throw new HttpError(404, "Cliente no encontrado.");
    await prisma.cliente.delete({ where: { id } });
    res.json({ data: { id, eliminado: true } });
  })
);

export default router;
