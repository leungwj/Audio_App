"use server";
import { redirect } from 'next/navigation'
import { createSession } from './session';

export async function authenticate(  prevState: string | undefined, formData: FormData) {
    const redirectTo = formData.get('redirectTo') as string;

    try {
        // Step 1: get the email and password from the form data
        const credentials = new URLSearchParams({ 
            username: formData.get('username') as string, 
            password: formData.get('password') as string 
        }).toString();

        // Step 2: Submit form data to backend server
        const response = await fetch(`http://localhost:8000/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: credentials
        });

        const response_data = await response.json();
        
        if (!response.ok) {
            return response_data.detail;
        }

        // TODO: Set cookie with token details
        const success = await createSession(response_data.access_token);

        if (!success) {
            return "Error creating session. Please try again.";
        }
        
        console.log(response_data);

    } catch (error) {
        console.error("Error logging in:", error);
        return error;
    }

    if (redirectTo) {
        redirect(redirectTo);
    }
}

export async function register(  prevState: string | undefined, formData: FormData) {
    const redirectTo = formData.get('redirectTo') as string;

    try {
        // Step 1: get the username, full_name, email, and password from the form data
        const credentials = new URLSearchParams({ 
            username: formData.get('username') as string, 
            full_name: formData.get('full_name') as string, 
            email: formData.get('email') as string, 
            password: formData.get('password') as string 
        }).toString();

        // Step 2: Submit form data to backend server
        const response = await fetch(`http://localhost:8000/users/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: credentials
        });

        const response_data = await response.json();
        
        if (!response.ok) {
            return response_data.detail;
        }
        
        console.log(response_data);

    } catch (error) {
        console.error("Error signing up:", error);
        return error;
    }

    if (redirectTo) {
        redirect(redirectTo);
    }
}