import { PrismaClient } from "@prisma/client";

// Instancia única de PrismaClient compartida por toda la API.
const prisma = new PrismaClient();

export default prisma;
