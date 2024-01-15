import { Request, Response, NextFunction } from "express";
import { verify } from "jsonwebtoken";

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

        req.__jwt__userid = (decoded as any).userid;

        next();
    });
}