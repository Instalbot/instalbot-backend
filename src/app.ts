import dotenv from "dotenv";
import express from "express";

import router from "./routes/router";
import logger from "./logger";

dotenv.config();

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use("/api", router);

app.get("/", (req, res) => {
    res.json({ message: "Hello from backend", status: 200 });
});

app.get("/*", (req, res) => {
    res.status(404).json({ message: "Not found", status: 404 })
});

app.listen(3000, () => {
    logger.ready("Server is listening on port 3000");
});