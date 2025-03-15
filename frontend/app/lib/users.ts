"use server";

import { getSession } from "./session";

export async function getCurrentUser() {
    const session_token = await getSession();

    if (!session_token) {
        return "Error getting session token";
    }

    try {
        const response = await fetch(`http://localhost:8000/users`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${session_token.value}`
            }
        });

        const response_data = await response.json();
        
        if (!response.ok) {
            console.log(response_data.detail);
            return response_data.detail;
        }

        console.log(response_data);

        return response_data.obj;

    } catch (error) {
        console.error("Error logging in:", error);
        return error;
    }
}