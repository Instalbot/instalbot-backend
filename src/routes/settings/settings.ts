import { FastifyInstance, FastifyPluginOptions, FastifyPluginAsync } from "fastify";
import fastifyPlugin from "fastify-plugin";

import { initFlags, initWords, validateToken } from "../middlewares";
import { IFlag, updateFlags } from "../../database/flags";
import logger from "../../logger";

const hoursRangeRegex = new RegExp("\\[[\\d]{1,2},[ ]*.?[\\d]{1,2}\\]");

function checkHoursRange(hoursRange: string) {
    if (!hoursRangeRegex.test(hoursRange)) return false;

    const [start, end] = hoursRange.replace(/[\[\] ]/g, "").split(",");

    if (
        parseInt(start) > parseInt(end) ||
        parseInt(start) < 0 || parseInt(end) > 23
    ) return false;

    return true;
}

async function flagsRoute(api: FastifyInstance, options: FastifyPluginOptions) {
    api.addHook("preHandler", initFlags);

    api.get("/", async(request, reply) => {
        const user = request.__jwt__user;

        if (!user) {
            reply.status(500);
            return { message: "Internal Server Error", error: 1000, status: 500 };
        }

        const flags = user.flags;

        // @ts-ignore
        delete flags["instaling_pass"];

        return { message: "Success", flags, status: 200 };
    });

    api.put("/", async(request, reply) => {
        const user = request.__jwt__user;

        if (!request.__jwt__user || !user) {
            reply.status(500);
            return { message: "Internal Server Error", error: 1000, status: 500 };
        }

        const flags = user.flags;

        if (!flags) {
            reply.status(500);
            return { message: "Internal Server Error", error: 1009, status: 500 };
        }

        const toUpdate = Object.assign({
            hoursrange: flags.hoursrange,
            instaling_user: flags.instaling_user,
            instaling_pass: flags.instaling_pass,
            error_level: flags.error_level,
        }, request.body)

        // @ts-ignore
        delete toUpdate["todo"];
        // @ts-ignore
        delete toUpdate["userid"];

        if (!checkHoursRange(toUpdate.hoursrange)) {
            reply.status(400);
            return { message: "Bad request", error: "hoursrange format is not valid", status: 400 };
        }
        
        if (isNaN(parseInt((toUpdate.error_level as any)))) {
            reply.status(400);
            return { message: "Bad request", error: "error_level is not a number", status: 400 };
        }

        let result: IFlag;

        try {
            result = await updateFlags(user.userid || 0, toUpdate, flags.instaling_pass);
        } catch(err) {
            logger.error(`Error updating flags for user ${user.userid}: ${err}`);
            reply.status(500);
            return { message: "Internal Server Error", error: 1009, status: 500 };
        }

        request.__jwt__user.flags = result;

        // @ts-ignore
        delete result["instaling_pass"];

        return { message: "Success", flags: result, status: 200 };
    });
}

async function wordsRoute(api: FastifyInstance, options: FastifyPluginOptions) {
    api.addHook("preHandler", initWords);

    api.get("/", async(request, reply) => {
        const user = request.__jwt__user;

        if (!user) {
            reply.status(500);
            return { message: "Internal Server Error", error: 1000, status: 500 };
        }

        const words = user.words;

        return { message: "Success", words, status: 200 };
    });

    api.get("/request-scrape", async(request, reply) => {
        if (!request.__jwt__user || !request.__jwt__user.userid) {
            reply.status(500);
            return { message: "Internal Server Error", error: 1000, status: 500 };
        }

        //const client = await getClient();
        //const clientId = await client.CLIENT_ID();

        //client.lPush("task_queue", `SCRAPER-REQUEST-${clientId}-${request.__jwt__user.userid}`);

        return { message: "Success", status: 200 };
    });
}

async function router(api: FastifyInstance, options: FastifyPluginOptions) {
    api.addHook("preHandler", validateToken);

    const flagsRouter = fastifyPlugin(flagsRoute as FastifyPluginAsync, { encapsulate: true });
    const wordsRouter = fastifyPlugin(wordsRoute as FastifyPluginAsync, { encapsulate: true });

    api.register(flagsRouter, { prefix: "/flags" });
    api.register(wordsRouter, { prefix: "/words" });
}

export default fastifyPlugin(router as FastifyPluginAsync, { encapsulate: true });
