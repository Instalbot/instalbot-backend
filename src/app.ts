import dotenv from "dotenv";
import fastify from "fastify";
import cors from "@fastify/cors";

import router from "./routes/router";
import logger from "./logger";

import "./redis";

dotenv.config();

const server = fastify({
    logger: false
});

server.register(cors)

server.register(router, { prefix: "/api" });

server.listen({ port: 3000 }, (err) => {
    if (err) {
        logger.error(`Error while starting server: ${err}`);
        process.exit(1)
    } else {
        logger.ready(`Server listening on port 3000`);
    }
})