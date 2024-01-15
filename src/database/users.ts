import { PoolClient } from "pg";
import { getClient } from "./database";

export interface IUser {
    userid: number;
    email: string;
    password: string;
    username: string;
    created: Date;
    updated: Date;
}

export async function getUserById(userid: number, poolClient?: PoolClient): Promise<(IUser | undefined)> {
    try {
        const client = poolClient || await getClient();

        const result = await client.query("SELECT * FROM users WHERE userid = $1 LIMIT 1", [userid]);

        client.release();

        return (result.rows[0] as IUser) || undefined;
    } catch(err) {
        throw new Error(err as string);
    }
}

export async function getUserByEmail(email: string, poolClient?: PoolClient) {
    try {
        const client = poolClient || await getClient();

        const result = await client.query("SELECT * FROM users WHERE email = $1 LIMIT 1", [email]);

        client.release();

        return (result.rows[0] as IUser) || undefined;
    } catch(err) {
        throw new Error(err as string);
    }
}

export async function createUser(email: string, password: string, username: string, poolClient?: PoolClient) {
    try {
        const client = poolClient || await getClient();

        const result = await client.query("INSERT INTO users (email, password, username) VALUES ($1, $2, $3) RETURNING userid", [email, password, username]);

        client.release();

        return result.rows[0].userid as number;
    } catch(err) {
        throw new Error(err as string);
    }
}