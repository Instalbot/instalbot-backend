import { PoolClient } from "pg";
import { getClient } from "./database";

export interface IWord {
    userid: number;
    list: { key: string, value: string }[];
}

export async function getWords(userid: number, poolClient?: PoolClient) {
    try {
        const client = poolClient || await getClient();

        const result = await client.query("SELECT * FROM words WHERE userid = $1", [userid]);

        client.release();

        return (result.rows[0] as IWord) || undefined;
    } catch(err) {
        throw new Error(err as string);
    }
}

export async function createWords(userid: number, poolClient?: PoolClient) {
    try {
        const client = poolClient || await getClient();

        const result = await client.query("INSERT INTO words (userid) VALUES ($1) RETURNING *", [userid]);

        client.release();

        return result.rows[0] as IWord;
    } catch(err) {
        throw new Error(err as string);
    }
}