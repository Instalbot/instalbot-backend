import { FastifyInstance, FastifyPluginOptions, FastifyPluginAsync } from "fastify";
import fastifyPlugin from "fastify-plugin";

import { initFlags, initWords, validateToken } from "../middlewares";
import { createFlags, updateFlags } from "../../database/flags";
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

    api.post("/", async(request, reply) => {
        const user = request.__jwt__user;

        if (!request.__jwt__user || !user || !user.userid) {
            reply.status(500);
            return { message: "Internal Server Error", error: 1000, status: 500 };
        }

        let flag;

        try {
            flag = await createFlags(user.userid);
        } catch(err) {
            reply.status(500);
            return { message: "Internal Server Error", error: 1009, status: 500 };
        }

        if (user.flags)
            request.__jwt__user.flags?.push(flag);
        else {
            request.__jwt__user.flags = [];
            request.__jwt__user.flags.push(flag);
        }

        return { message: "Success", flags: flag, status: 200 };
    })

    api.put("/:flagid", async(request, reply) => {
        const user = request.__jwt__user;
        const { flagid } = request.params as { flagid?: string };
        
        if (!flagid || isNaN(parseInt(flagid))) {
            reply.status(400);
            return { message: "Request is missing 'flagid' parameter", error: 1021, status: 400 };
        }

        if (!request.__jwt__user || !user) {
            reply.status(500);
            return { message: "Internal Server Error", error: 1000, status: 500 };
        }

        const flags = user.flags;

        if (!request.__jwt__user.flags || !user.flags || !flags || !flags[0]) {
            reply.status(500);
            return { message: "Internal Server Error", error: 1009, status: 500 };
        }

        let flag = flags.find(x => x.flagid == parseInt(flagid));

        if (!flag) {
            reply.status(403);
            return { message: "Flag is not associated with your account", error: 1022, status: 403 };
        }

        const toUpdate = Object.assign(flag, request.body)

        // @ts-expect-error
        delete toUpdate["todo"];
        // @ts-expect-error
        delete toUpdate["userid"];
        // @ts-expect-error
        delete toUpdate["flagid"];

        if (!checkHoursRange(toUpdate.hoursrange)) {
            reply.status(400);
            return { message: "Bad request", error: "hoursrange format is not valid", status: 400 };
        }
        
        if (isNaN(parseInt((toUpdate.error_level as any)))) {
            reply.status(400);
            return { message: "Bad request", error: "error_level is not a number", status: 400 };
        }

        try {
            flag = await updateFlags(parseInt(flagid), toUpdate, flag.instaling_pass);
        } catch(err) {
            logger.error(`Error updating flags for user ${user.userid}: ${err}`);
            reply.status(500);
            return { message: "Internal Server Error", error: 1009, status: 500 };
        }

        const index = flags.findIndex(x => x.flagid == flag?.flagid);

        request.__jwt__user.flags[index] = flag;

        // @ts-expect-error
        delete flag["instaling_pass"];

        return { message: "Success", flags: flag, status: 200 };
    });
}

async function wordsRoute(api: FastifyInstance, options: FastifyPluginOptions) {
    api.addHook("preHandler", initFlags);
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
