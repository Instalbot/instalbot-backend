import { Router } from "express";
import { hash, verify } from "argon2";
import { sign } from "jsonwebtoken";
import { cpus } from "os";

import { validateToken } from "../middlewares";
import { IUser, createUser, getUserByEmail } from "../../database/users";
import logger from "../../logger";

const router = Router();

router.post("/login", async(req, res) => {
    const body = req.body;

    if (!body.email || !body.password)
        return res.status(400).json({ message: "Bad Request", error: "Missing email or password", status: 400 });

    let user: IUser | undefined;

    try {
        user = await getUserByEmail(body.email);
    } catch(err) {
        logger.error(`Error while getting user by email: ${err}`)
        return res.status(500).json({ message: "Internal Server Error", error: 0, status: 500 });
    }

    if (!user)
        return res.status(401).json({ message: "Unauthorized", error: "Invalid email or password", status: 401 });

    let valid = false;

    try {
        valid = await verify(user.password, body.password);
    } catch(err) {
        return res.status(401).json({ message: "Unauthorized", error: "Invalid email or password", status: 401 });
    }

    if (!valid)
        return res.status(401).json({ message: "Unauthorized", error: "Invalid email or password", status: 401 });

    const token = sign({ userid: user.userid }, process.env.JWT_SECRET as string, {
        algorithm: "HS512",
        expiresIn: "1h"
    });

    res.json({ message: "Success", token, status: 200 });
});

router.post("/register", async(req, res) => {
    const body = req.body;

    if (!body.email || !body.password || !body.username)
        return res.status(400).json({ message: "Bad Request", error: "Missing email, password or username", status: 400 });

    let user: IUser | undefined;

    try {
        user = await getUserByEmail(body.email);
    } catch(err) {
        logger.error(`Error while getting user by email: ${err}`)
        return res.status(500).json({ message: "Internal Server Error", error: 0, status: 500 });
    }

    if (user)
        return res.status(401).json({ message: "Bad Request", error: "User already exists", status: 400 });

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
        return res.status(500).json({ message: "Internal Server Error", error: 1, status: 500 });
    }

    let userid: number;

    try {
        userid = await createUser(body.email, password, body.username);
    } catch(err) {
        logger.error(`Error while creating user: ${err}`);
        return res.status(500).json({ message: "Internal Server Error", error: 2, status: 500 });
    }

    res.json({ message: "Success", userid, status: 200 });
});

router.get("/", validateToken, async(req, res) => {
    const userid = req.__jwt__userid;

    if (!userid)
        return res.status(500).json({ message: "Internal Server Error", error: 0, status: 500 });

    res.json({ message: "Success", userid, status: 200 });
});

export default router;