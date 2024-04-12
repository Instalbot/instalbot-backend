import dotenv from "dotenv";
import fastify from "fastify";
import cors from "@fastify/cors";

import router from "./routes/router";
import logger from "./logger";

dotenv.config();

const server = fastify({
    logger: false,
    trustProxy: true,
});

server.register(cors);

server.register(router, { prefix: "/api" });

server.listen({ port: 3000, host: "0.0.0.0" }, (err) => {
    if (err) {
        logger.error(`Error while starting server: ${err}`);
        process.exit(1);
    } else {
        logger.ready(`Server listening on port 3000`);
    }
});
