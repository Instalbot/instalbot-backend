import { FastifyInstance, FastifyPluginOptions, FastifyPluginAsync, DoneFuncWithErrOrRes } from "fastify";
import fastifyPlugin from "fastify-plugin";

import settings from "./settings/settings";
import users from "./users/users";
import { IFlag } from "../database/flags";
import { IWord } from "../database/words";


declare module 'fastify' {
    export interface FastifyRequest  {
        __jwt__user?: {
            userid?: number,
            flags?: IFlag[]
            words?: IWord[]
        }
    }
}

async function initRouter(api: FastifyInstance, options: FastifyPluginOptions, done: DoneFuncWithErrOrRes) {
    api.register(settings, { prefix: "/settings" });
    api.register(users, { prefix: "/users" });

    done();
}

export default fastifyPlugin(initRouter as FastifyPluginAsync, { encapsulate: true });