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
const ESTADOS_LABORALES = ["Activo", "Inactivo", "Vacaciones"];
const CAMPOS_OBLIGATORIOS = [
  "nombres",
  "apellidos",
  "tipo_documento",
  "numero_documento",
  "cargo",
  "telefono",
  "correo",
  "fecha_contratacion",
  "estado_laboral",
];

function aFecha(valor, campo) {
  const fecha = new Date(valor);
  if (Number.isNaN(fecha.getTime())) {
    throw new HttpError(400, `El campo '${campo}' debe ser una fecha válida (AAAA-MM-DD).`);
  }
  return fecha;
}

function normalizar(body = {}) {
  requeridos(CAMPOS_OBLIGATORIOS, body);
  return {
    nombres: String(body.nombres).trim(),
    apellidos: String(body.apellidos).trim(),
    tipoDocumento: enumValido(String(body.tipo_documento).trim(), TIPOS_DOCUMENTO, "tipo_documento"),
    numeroDocumento: String(body.numero_documento).trim(),
    cargo: String(body.cargo).trim(),
    telefono: String(body.telefono).trim(),
    correo: String(body.correo).trim(),
    fechaContratacion: aFecha(body.fecha_contratacion, "fecha_contratacion"),
    estadoLaboral: enumValido(String(body.estado_laboral).trim(), ESTADOS_LABORALES, "estado_laboral"),
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
        { cargo: { contains: termino } },
      ];
    }
    if (req.query.estado_laboral) {
      where.estadoLaboral = enumValido(
        String(req.query.estado_laboral).trim(),
        ESTADOS_LABORALES,
        "estado_laboral"
      );
    }
    const [data, total] = await Promise.all([
      prisma.empleado.findMany({
        where,
        orderBy: [{ apellidos: "asc" }, { nombres: "asc" }],
        skip: pag.skip,
        take: pag.limite,
      }),
      prisma.empleado.count({ where }),
    ]);
    res.json(respuestaPaginada(data, total, pag));
  })
);

router.get(
  "/:id",
  asyncHandler(async (req, res) => {
    const empleado = await prisma.empleado.findUnique({ where: { id: idNumerico(req.params.id) } });
    if (!empleado) throw new HttpError(404, "Empleado no encontrado.");
    res.json({ data: empleado });
  })
);

router.post(
  "/",
  asyncHandler(async (req, res) => {
    const empleado = await prisma.empleado.create({ data: normalizar(req.body) });
    res.status(201).json({ data: empleado });
  })
);

router.put(
  "/:id",
  asyncHandler(async (req, res) => {
    const empleado = await prisma.empleado.update({
      where: { id: idNumerico(req.params.id) },
      data: normalizar(req.body),
    });
    res.json({ data: empleado });
  })
);

router.delete(
  "/:id",
  asyncHandler(async (req, res) => {
    const id = idNumerico(req.params.id);
    const existe = await prisma.empleado.findUnique({ where: { id }, select: { id: true } });
    if (!existe) throw new HttpError(404, "Empleado no encontrado.");
    await prisma.empleado.delete({ where: { id } });
    res.json({ data: { id, eliminado: true } });
  })
);

export default router;
