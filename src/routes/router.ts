import { NextFunction, Request, Response, Router } from "express";
import { verify, sign } from "jsonwebtoken";

import settings from "./settings/settings";
import users from "./users/users";

declare global {
    namespace Express {
        export interface Request {
            __jwt__user?: {
                userid: number;
            }
        }
    }
}

// JWT validation middleware
export function validateToken(req: Request, res: Response, next: NextFunction) {
    const authorizationHeader = req.headers["authorization"];

    if (!authorizationHeader)
        return res.status(401).json({ message: "Unauthorized", error: "Authorization header not present in request", status: 401 });

    const split = authorizationHeader.split(" ");
    const type = split[0];
    const token = split[1];

    if (type !== "Bearer")
        return res.status(401).json({ message: "Unauthorized", error: "Authorization header is invalid type", status: 401 });

    if (!token)
        return res.status(401).json({ message: "Unauthorized", error: "Token not present in authorization header", status: 401 });

    verify(token, process.env.JWT_SECRET as string, (err, decoded) => {
        if (err)
            return res.status(401).json({ message: "Unauthorized", error: err.message, status: 401 });

        req.__jwt__user = (decoded as any).userid;

        next();
    });
}

const router = Router();

router.use("settings", validateToken, settings);
router.use("users", users);

export default router;