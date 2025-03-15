// import { SignupFormSchema, FormState } from "@/lib/definitions";
"use server";

export async function login(formData: FormData) {
    try {
        // Step 1: get the email and password from the form data
        const data = new URLSearchParams({ 
            email: formData.get('email') as string, 
            password: formData.get('password') as string 
        }).toString();

        // Step 2: Submit form data to backend server
        const response = await fetch(`${process.env.API_SERVER}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: data
        });

        // Step 3: If response successful, inject access token into cookies, then redirect to homepage
        
    }
    catch (error) {
        console.error("Error logging in", error);
        return {
            error: "Please try again later"
        }
    }
}

export async function signup(formData: FormData) {
    try {
        // Step 1: get the username, full_name, email, and password from the form data
        const data = new URLSearchParams({ 
            username: formData.get('username') as string, 
            full_name: formData.get('full_name') as string, 
            email: formData.get('email') as string, 
            password: formData.get('password') as string 
        }).toString();

        // Step 2: Submit form data to backend server
        const response = await fetch(`${process.env.API_SERVER}/users/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: data
        });

        if (response.ok){
            const data = await response.json();
            return {
                message: "User created successfully at " + data.created_at
            };
        }
        else {
            const error = await response.json();
            return {
                error: "Error: " + error.detail
            };
        }
    } catch (error) {
        console.error("Error signing up", error);
        return {
            error: "Please try again later"
        }
    }
}