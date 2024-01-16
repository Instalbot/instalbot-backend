import { createClient } from "redis";
import logger from "./logger";

import dotenv from "dotenv";
dotenv.config();

const client =
    createClient({
        socket: {
            host: process.env.REDIS_HOST,
            port: parseInt(process.env.REDIS_PORT as string)
        },
        password: process.env.REDIS_PASSWORD,
    })
    .on("error", err => {
        logger.error("Redis Client Error", err);
        process.exit(1);
    })
    .connect();

export function getClient() {
    return client;
}
