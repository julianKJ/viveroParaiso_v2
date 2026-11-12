document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("sidebar");
    const backdrop = document.querySelector(".sidebar-backdrop");
    document.querySelectorAll("[data-toggle-sidebar]").forEach((button) => {
        button.addEventListener("click", () => {
            sidebar?.classList.toggle("open");
            backdrop?.classList.toggle("open");
        });
    });

    document.querySelectorAll(".js-confirm-delete").forEach((form) => {
        form.addEventListener("submit", (event) => {
            const message = form.getAttribute("data-message") || "¿Confirma que desea eliminar este registro?";
            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });

    document.querySelectorAll("form[novalidate]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (!form.checkValidity()) {
                event.preventDefault();
                const firstInvalid = form.querySelector(":invalid");
                firstInvalid?.reportValidity();
            }
        });
    });

    // input type="number" acepta e, E, + y - (notación científica); aquí solo se permiten dígitos.
    document.querySelectorAll('input[type="number"]').forEach((input) => {
        const entero = input.step === "1";
        const bloqueadas = entero ? ["e", "E", "+", "-", ".", ","] : ["e", "E", "+", "-"];
        const valido = entero ? /^\d+$/ : /^\d+([.,]\d{1,2})?$/;
        const prohibido = entero ? /[^0-9]/ : /[^0-9.,]/;
        input.addEventListener("keydown", (event) => {
            if (bloqueadas.includes(event.key)) {
                event.preventDefault();
            }
        });
        // Cubre teclados de celular y autocompletado, que no siempre disparan keydown.
        input.addEventListener("beforeinput", (event) => {
            if (event.data && prohibido.test(event.data)) {
                event.preventDefault();
            }
        });
        input.addEventListener("paste", (event) => {
            const texto = (event.clipboardData || window.clipboardData).getData("text").trim();
            if (!valido.test(texto)) {
                event.preventDefault();
            }
        });
        input.addEventListener("drop", (event) => event.preventDefault());
    });

    document.querySelectorAll('input[type="tel"]').forEach((input) => {
        input.addEventListener("input", () => {
            const limpio = input.value.replace(/[^0-9+\-\s()]/g, "");
            if (limpio !== input.value) {
                input.value = limpio;
            }
        });
    });

    document.querySelectorAll("[data-print]").forEach((boton) => {
        boton.addEventListener("click", () => window.print());
    });

    // Formulario de venta: muestra precio, stock y total mientras se elige.
    const formVenta = document.querySelector("[data-venta-form]");
    if (formVenta) {
        const producto = formVenta.querySelector("[data-producto]");
        const cantidad = formVenta.querySelector("[data-cantidad]");
        const pesos = new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 });
        const campo = (nombre) => document.querySelector(`[data-resumen-${nombre}]`);
        const actualizar = () => {
            const opcion = producto.selectedOptions[0];
            const precio = Number(opcion?.dataset.precio || 0);
            const stock = Number(opcion?.dataset.stock || 0);
            const unidades = Number(cantidad.value || 0);
            if (!opcion || !opcion.value) {
                ["precio", "stock", "restante", "total"].forEach((n) => { campo(n).textContent = "—"; });
                cantidad.removeAttribute("max");
                return;
            }
            cantidad.max = String(stock);
            campo("precio").textContent = pesos.format(precio);
            campo("stock").textContent = `${stock} unidad(es)`;
            const restante = stock - unidades;
            campo("restante").textContent = restante >= 0 ? `${restante} unidad(es)` : "Stock insuficiente";
            campo("total").textContent = pesos.format(precio * unidades);
        };
        producto.addEventListener("change", actualizar);
        cantidad.addEventListener("input", actualizar);
        actualizar();
    }

    const indicadoresApi = document.querySelectorAll("[data-api-status]");
    if (indicadoresApi.length && window.ViveroAPI) {
        window.ViveroAPI.salud()
            .then(() => {
                indicadoresApi.forEach((el) => {
                    el.dataset.apiStatus = "ok";
                    el.textContent = "API conectada";
                });
            })
            .catch(() => {
                indicadoresApi.forEach((el) => {
                    el.dataset.apiStatus = "error";
                    el.textContent = "API no disponible";
                });
            });
    }

    setTimeout(() => {
        document.querySelectorAll(".flash-stack .flash").forEach((el) => {
            el.style.opacity = "0";
            el.style.transition = "opacity 0.4s ease";
        });
    }, 5000);
});
