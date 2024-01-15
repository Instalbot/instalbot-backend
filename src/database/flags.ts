import { PoolClient } from "pg";
import { getClient } from "./database";

export interface IFlag {
    userid: number;
    todo: boolean;
    instaling_user: string;
    instaling_pass: string;
    error_level: number;
    hoursrange: `[${number}, ${number}]`
}

export function xorEncryption(text: string, key: string): string {
    let encryptedText = "";

    for (let i = 0; i < text.length; i++) {
        encryptedText += String.fromCharCode(
            text.charCodeAt(i) ^ key.charCodeAt(i % key.length)
        );
    }

    return encryptedText;
}

export async function getFlags(userid: number, poolClient?: PoolClient) {
    try {
        const client = poolClient || await getClient();

        const result = await client.query("SELECT * FROM flags WHERE userid = $1", [userid]);

        client.release();

        return (result.rows[0] as IFlag) || undefined;
    } catch(err) {
        throw new Error(err as string);
    }
}

export async function createFlags(userid: number, poolClient?: PoolClient) {
    try {
        const client = poolClient || await getClient();

        const result = await client.query("INSERT INTO flags (userid) VALUES ($1) RETURNING *", [userid]);

        client.release();

        return result.rows[0] as IFlag;
    } catch(err) {
        throw new Error(err as string);
    }
}

export async function updateFlags(userid: number, flags: any, oldPassword: string, poolClient?: PoolClient) {
    try {
        const client = poolClient || await getClient();
        let password = "";

        if (flags.instaling_pass !== oldPassword) {
            if (!process.env.INSTALING_KEY)
                throw new Error("INSTALING_KEY is not defined");

            password = xorEncryption(flags.instaling_pass, process.env.INSTALING_KEY);
        } else {
            password = oldPassword;
        }

        const result = await client.query("UPDATE flags SET todo = $1, instaling_user = $2, instaling_pass = $3, error_level = $4, hoursrange = $5 WHERE userid = $6 RETURNING *", [
            true,
            flags.instaling_user,
            password,
            flags.error_level,
            flags.hoursrange,
            userid
        ]);

        client.release();

        return result.rows[0] as IFlag;
    } catch(err) {
        throw new Error(err as string);
    }
}