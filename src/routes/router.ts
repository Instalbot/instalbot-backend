import { Router } from "express";

import { validateToken } from "./middlewares";
import settings from "./settings/settings";
import users from "./users/users";

declare global {
    namespace Express {
        export interface Request {
            __jwt__userid?: number
        }
    }
}

const router = Router();

router.use("/settings", validateToken, settings);
router.use("/users", users);

export default router;