
 * Cliente JavaScript para la API Node.js + Express + Prisma.
 *
 * La URL base se inyecta desde Flask en base.html (window.VIVERO_API_URL),
 * por lo que si cambia el puerto de la API solo se ajusta el .env raíz.
 *
 * Ejemplos de uso:
 *   const { data, total } = await ViveroAPI.productos.listar({ q: "cactus", page: 1 });
 *   await ViveroAPI.productos.crear({ nombre: "Helecho", categoria: "Interior", ... });
 *   const { data } = await ViveroAPI.dashboard.resumen();
 */
(function () {
    const BASE_URL = (window.VIVERO_API_URL || "http://127.0.0.1:4000/api").replace(/\/+$/, "");

    function cadenaConsulta(params) {
        if (!params) return "";
        const busqueda = new URLSearchParams();
        Object.entries(params).forEach(([clave, valor]) => {
            if (valor !== undefined && valor !== null && valor !== "") {
                busqueda.append(clave, valor);
            }
        });
        const cadena = busqueda.toString();
        return cadena ? `?${cadena}` : "";
    }

    async function peticion(ruta, { method = "GET", body, params } = {}) {
        const respuesta = await fetch(`${BASE_URL}${ruta}${cadenaConsulta(params)}`, {
            method,
            headers: { "Content-Type": "application/json" },
            body: body === undefined ? undefined : JSON.stringify(body),
        });

        const texto = await respuesta.text();
        const datos = texto ? JSON.parse(texto) : null;

        if (!respuesta.ok) {
            const error = new Error((datos && datos.error) || `Error HTTP ${respuesta.status}`);
            error.status = respuesta.status;
            error.detalles = (datos && datos.detalles) || null;
            throw error;
        }
        return datos;
    }

    function recurso(base) {
        return {
            listar: (params) => peticion(base, { params }),
            obtener: (id) => peticion(`${base}/${id}`),
            crear: (body) => peticion(base, { method: "POST", body }),
            actualizar: (id, body) => peticion(`${base}/${id}`, { method: "PUT", body }),
            eliminar: (id) => peticion(`${base}/${id}`, { method: "DELETE" }),
        };
    }

    window.ViveroAPI = {
        baseUrl: BASE_URL,
        peticion,
        salud: () => peticion("/health"),
        dashboard: { resumen: () => peticion("/dashboard/resumen") },
        productos: Object.assign(recurso("/productos"), {
            categorias: () => peticion("/productos/categorias"),
        }),
        clientes: recurso("/clientes"),
        empleados: recurso("/empleados"),
        proveedores: Object.assign(recurso("/proveedores"), {
            activos: () => peticion("/proveedores/activos"),
        }),
    };
})();
