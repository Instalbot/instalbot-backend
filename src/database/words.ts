import { PoolClient } from "pg";
import { getClient } from "./database";

export interface IWord {
    userid: number;
    flagid: number;
    list: { key: string, value: string }[];
}

export async function getWords(userid: number, poolClient?: PoolClient) {
    try {
        const client = poolClient || await getClient();

        const result = await client.query("SELECT * FROM words WHERE userid = $1", [userid]);

        client.release();

        return result.rows as IWord[];
    } catch(err) {
        throw new Error(err as string);
    }
}

export async function getWordsByFlagId(flagid: number, poolClient?: PoolClient) {
    try {
        const client = poolClient || await getClient();

        const result = await client.query("SELECT * FROM words WHERE flagid = $1", [flagid]);

        client.release();

        return (result.rows[0] as IWord) || undefined;
    } catch(err){
        throw new Error(err as string);
    }
}

export async function createWords(flagid: number, userid: number, poolClient?: PoolClient) {
    try {
        const client = poolClient || await getClient();

        const result = await client.query("INSERT INTO words (flagid, userid) VALUES ($1, $2) RETURNING *", [flagid, userid]);

        client.release();

        return result.rows[0] as IWord;
    } catch(err) {
        throw new Error(err as string);
    }
}