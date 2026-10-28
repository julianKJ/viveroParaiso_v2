// Utilidades compartidas por las rutas de la API.

export class HttpError extends Error {
  constructor(status, mensaje, detalles = null) {
    super(mensaje);
    this.status = status;
    this.detalles = detalles;
  }
}

// Envuelve un handler async para que los errores lleguen al middleware de errores.
export const asyncHandler = (handler) => (req, res, next) =>
  Promise.resolve(handler(req, res, next)).catch(next);

export function paginacion(query = {}, itemsPorDefecto = 10) {
  const page = Math.max(Number.parseInt(query.page, 10) || 1, 1);
  const limite = Math.min(Math.max(Number.parseInt(query.limit, 10) || itemsPorDefecto, 1), 100);
  return { page, limite, skip: (page - 1) * limite };
}

export function respuestaPaginada(data, total, { page, limite }) {
  return { data, total, page, limite, paginas: Math.ceil(total / limite) };
}

export function idNumerico(valor, campo = "id") {
  const numero = Number(valor);
  if (!Number.isInteger(numero) || numero <= 0) {
    throw new HttpError(400, `El campo '${campo}' debe ser un entero positivo.`);
  }
  return numero;
}

export function aEntero(valor, campo, { minimo = 0 } = {}) {
  const numero = Number(valor);
  if (!Number.isInteger(numero) || numero < minimo) {
    throw new HttpError(400, `El campo '${campo}' debe ser un entero mayor o igual a ${minimo}.`);
  }
  return numero;
}

export function aDecimal(valor, campo, { minimo = 0 } = {}) {
  const numero = Number(valor);
  if (!Number.isFinite(numero) || numero < minimo) {
    throw new HttpError(400, `El campo '${campo}' debe ser un número mayor o igual a ${minimo}.`);
  }
  return numero;
}

export function textoOpcional(valor) {
  if (valor === undefined || valor === null) return null;
  const texto = String(valor).trim();
  return texto === "" ? null : texto;
}

export function requeridos(campos, body = {}) {
  const faltantes = campos.filter((campo) => {
    const valor = body[campo];
    return valor === undefined || valor === null || String(valor).trim() === "";
  });
  if (faltantes.length > 0) {
    throw new HttpError(400, `Campos obligatorios faltantes: ${faltantes.join(", ")}.`);
  }
}

export function enumValido(valor, permitidos, campo) {
  if (!permitidos.includes(valor)) {
    throw new HttpError(400, `El campo '${campo}' solo acepta: ${permitidos.join(", ")}.`);
  }
  return valor;
}
