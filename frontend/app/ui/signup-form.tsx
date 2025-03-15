"use client";

import { useState } from 'react';
import { signup } from '@/app/lib/auth';

export function SignupForm(){
    // used for displaying validation errors
    const [state, setState] = useState({ message: '', error: '' });
    const [pending, setPending] = useState(false);

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        // Step 1: Prevent the default form submission behaviour
        event.preventDefault();
        setPending(true); // submission started
        const formData = new FormData(event.currentTarget); // copy the form data

        const result = await signup(formData);
        setPending(false); // submission finished

        setState({ message: result.message, error: result.error ? result.error : '' });
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex flex-col">
                <label htmlFor="username" className="mb-2 font-medium text-gray-700">Username</label>
                <input id="username" name="username" placeholder="Username" className="p-2 border border-gray-300 rounded" required />
            </div>

            <div className="flex flex-col">
                <label htmlFor="full_name" className="mb-2 font-medium text-gray-700">Full Name</label>
                <input id="full_name" name="full_name" placeholder="Full Name" className="p-2 border border-gray-300 rounded" required />
            </div>

            <div className="flex flex-col">
                <label htmlFor="email" className="mb-2 font-medium text-gray-700">Email</label>
                <input id="email" name="email" type="email" placeholder="Email" className="p-2 border border-gray-300 rounded" required />
            </div>

            <div className="flex flex-col">
                <label htmlFor="password" className="mb-2 font-medium text-gray-700">Password</label>
                <input id="password" name="password" type="password" className="p-2 border border-gray-300 rounded" required />
            </div>

            <button disabled={pending} type="submit" className="w-full p-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400">
                Sign up
            </button>

            {state.message && <div className="success text-green-500 mt-2">{state.message}</div>}
            {state.error && <div className="error text-red-500 mt-2">{state.error}</div>}
        </form>
    )
}