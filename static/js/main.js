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
