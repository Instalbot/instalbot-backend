import { Router } from "express";
import { validateToken } from "../router";

const router = Router();

router.post("/login", (req, res) => {
});

router.post("/register", (req, res) => {
});

router.get("/", validateToken, (req, res) => {
});

export default router;