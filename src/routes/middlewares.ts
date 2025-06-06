import { FastifyRequest, FastifyReply, HookHandlerDoneFunction } from "fastify";
import { verify } from "jsonwebtoken";

import { createFlags, getFlags } from "../database/flags";
import logger from "../logger";
import { IWord, createWords, getWords, getWordsByFlagId } from "../database/words";

export async function validateToken(request: FastifyRequest, reply: FastifyReply) {
    const authorizationHeader = request.headers["authorization"];

    if (!authorizationHeader) {
        reply.status(401).send({ message: "Unauthorized", error: "Authorization header not present in request", status: 401 });
        throw new Error("Unauthorized");
    }

    const split = authorizationHeader.split(" ");
    const type = split[0];
    const token = split[1];

    if (type !== "Bearer") {
        reply.status(401).send({ message: "Unauthorized", error: "Authorization header is invalid type", status: 401 });
        throw new Error("Unauthorized");
    }

    if (!token) {
        reply.status(401).send({ message: "Unauthorized", error: "Token not present in authorization header", status: 401 });
        throw new Error("Unauthorized");
    }

    verify(token, process.env.JWT_SECRET as string, (err, decoded) => {
        if (err) {
            reply.status(401).send({ message: "Unauthorized", error: err.message, status: 401 });
            throw new Error("Unauthorized");
        }

        request.__jwt__user = {};
        request.__jwt__user.userid = (decoded as any).userid;
    });
}

export async function initFlags(request: FastifyRequest, reply: FastifyReply) {
    const req_userid = request.__jwt__user?.userid;

    if (!request.__jwt__user || !req_userid) {
        reply.status(500);
        return { message: "Internal Server Error", error: 1003, status: 500 };
    }

    let flags = await getFlags(req_userid);

    try {
        if (!flags[0])
            flags.push(await createFlags(req_userid));
    } catch(err) {
        logger.error(`initFlags(): Error while creating flags: ${err}`);

        reply.status(500);
        return { message: "Internal Server Error", error: 1001, status: 500 };
    }

    request.__jwt__user.flags = flags;
}

// TODO: rewrite words to use multiple flags
export async function initWords(request: FastifyRequest, reply: FastifyReply) {
    const user = request.__jwt__user;

    if (!request.__jwt__user || !user || !user.userid || !user.flags) {
        reply.status(500);
        return { message: "Internal Server Error", error: 1003, status: 500 };
    }

    let words: IWord[] = [];

    try {
        words = await getWords(user.userid);
    } catch(err) {
        logger.error(`Error while creating words: ${err}`);
        reply.status(500);
        return { message: "Internal Server Error", error: 1019, status: 500 };
    }

    if (user.flags.length > words.length) {
        try {
            user.flags.forEach(async user => {
                const wordsById = await getWordsByFlagId(user.flagid);

                if (!wordsById)
                    words.push(await createWords(user.flagid, user.userid));
            });
        } catch(err) {
            logger.error(`Error while creating words: ${err}`);
            reply.status(500);
            return { message: "Internal Server Error", error: 1011, status: 500 };
        }
    }

    request.__jwt__user.words = words;
}