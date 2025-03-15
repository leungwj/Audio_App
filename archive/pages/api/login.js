// Next.js API route support: https://nextjs.org/docs/api-routes/introduction

// export default function hello(req, res) {
//     res.status(200).json({ name: "John Doe" });
// }
import { cookie } from 
import { serialize } from 'cookie';

export default async function handler(req, res) {
    if (req.method === 'POST') {
        const { username, password } = req.body;

        const response = await fetch(`${process.env.API_SERVER}/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'accept': 'application/json'
            },
            body: new URLSearchParams({
                grant_type: '',
                username: username,
                password: password,
                scope: '',
                client_id: '',
                client_secret: ''
            })
        })
        
        if (response.ok) {
            const data = await response.json();
            const cookie = serialize(
                'session',
                JSON.stringify({
                    access_token: data.access_token,
                    token_type: data.token_type
                }),
                {
                    httpOnly: true,
                    secure: process.env.NODE_ENV === 'production',
                    maxAge: 60 * 30, // 30 minutes
                    path: '/'
                }
            );
            res.setHeader('Set-Cookie', cookie);
            res.status(200).json({ message: 'Login successful' });
        }
        else {
            const data = await response.json();
            res.status(401).json({ message: data.detail });
        }
    } else {
        res.setHeader('Allow', ['POST']);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
}