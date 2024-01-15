import { FastifyInstance, FastifyPluginOptions, FastifyPluginAsync } from "fastify";
import fastifyPlugin from "fastify-plugin";
import { hash, verify } from "argon2";
import { sign } from "jsonwebtoken";
import { cpus } from "os";

import { validateToken } from "../middlewares";
import { IUser, createUser, getUserByEmail } from "../../database/users";
import logger from "../../logger";

interface UserLoginRequestBody {
    email?: string;
    password?: string;
}

interface UserRegisterRequestBody extends UserLoginRequestBody {
    username?: string;
}

async function usersRoute(api: FastifyInstance, options: FastifyPluginOptions) {
    api.post("/login", async(request, reply) => {
        const body = request.body as UserLoginRequestBody;

        if (!body.email || !body.password) {
            reply.status(400);
            return { message: "Bad request", error: "Missing email or password", status: 400 };
        }

        let user;
        try {
            user = await getUserByEmail(body.email);
        } catch (err) {
            logger.error(`Error while getting user by email: ${err}`)
            reply.status(500);
            return { message: "Internal Server Error", error: "Error while getting user by email", status: 500 };
        }

        if (!user) {
            reply.status(401);
            return { message: "Unauthorized", error: "Invalid email or password", status: 401 };
        }

        let valid;
        try {
            valid = await verify(user.password, body.password);
        } catch (err) {
            reply.status(401);
            return { message: "Unauthorized", error: "Invalid email or password", status: 401 };
        }

        if (!valid) {
            reply.status(401);
            return { message: "Unauthorized", error: "Invalid email or password", status: 401 };
        }

        const token = sign({ userid: user.userid }, process.env.JWT_SECRET as string, { expiresIn: "1h", algorithm: "HS512" });

        return { message: "Success", token, status: 200 };
    });

    api.post("/register", async(request, reply) => {
        const body = request.body as UserRegisterRequestBody;

        if (!body.email || !body.password || !body.username) {
            reply.status(400);
            return { message: "Bad request", error: "Missing email, password or username", status: 400 };
        }

        let user: IUser | undefined;

        try {
            user = await getUserByEmail(body.email);
        } catch(err) {
            logger.error(`Error while getting user by email: ${err}`)
            reply.status(500);
            return { message: "Internal Server Error", error: "Error while getting user by email", status: 500 };
        }

        if (user) {
            reply.status(400);
            return { message: "Bad request", error: "User already exists", status: 400 };
        }

        let password: string;

        try {
            password = await hash(body.password, {
                hashLength: 32,
                memoryCost: 2 ** 16,
                parallelism: cpus().length * 2,
                timeCost: 4
            })
        } catch(err) {
            logger.error(`Error while hashing password: ${err}`);
            reply.status(500);
            return { message: "Internal Server Error", error: "Error while hashing password", status: 500 };
        }

        let userid: number;

        try {
            userid = await createUser(body.email, password, body.username);
        } catch(err) {
            logger.error(`Error while creating user: ${err}`);
            reply.status(500);
            return { message: "Internal Server Error", error: "Error while creating user", status: 500 };
        }

        return { message: "Success", userid, status: 200 };
    });

    api.get("/", {
        preHandler: validateToken,
    }, async(request, reply) => {
        const userid = request.__jwt__user?.userid;

        if (!userid) {
            reply.status(500);
            return { message: "Internal Server Error", error: "Userid not present in request", status: 500 };
        }

        return { message: "Success", userid, status: 200 };
    });
}

export default fastifyPlugin(usersRoute as FastifyPluginAsync, { encapsulate: true });