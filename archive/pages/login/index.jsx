import Head from "next/head";
import { FormEvent } from 'react';
import { useRouter } from 'next/router';

export default function LoginPage() {
    const router = useRouter();

    async function handleSubmit(event){
        event.preventDefault();
        // prevent the default form submission behavior, which is to define the route in the action attribute of the form element

        const formData = new FormData(event.currentTarget);
        // create a new FormData object from the form element
        // FormData objects provide a way to easily construct a set of key/value pairs representing form fields and their values

        const username = formData.get('username');
        const password = formData.get('password');

        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const data = await response.json();
            console.log("Message: ", data.message);
        } else {
            console.error('Login failed');
        }

    }

    return (
        <form onSubmit={handleSubmit}>
            <input type="text" name="username" placeholder="Username" required />
            <input type="password" name="password" placeholder="Password" required />
            <button type="submit">Login</button>
        </form>
    )
}