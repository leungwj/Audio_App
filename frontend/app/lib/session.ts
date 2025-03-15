import { cookies } from 'next/headers';

export async function isLoggedIn() {
    const cookieStore = await cookies();
    
    return cookieStore.has('session_token');
}

export async function getSession() {
    try {
        const cookieStore = await cookies();
    
        return cookieStore.get('session_token');
    } catch (error) {
        console.error("Error getting session:", error);
        return null;
    }
}

export async function createSession(access_token: string) {
    try {
        const expiresAt = new Date(Date.now() + 30 * 60 * 1000)

        const cookieStore = await cookies();
    
        cookieStore.set('session_token', access_token, {
        httpOnly: true,
        // secure: true,
        expires: expiresAt,
        sameSite: 'lax',
        path: '/',
        })

        return true;
    }
    catch (error) {
        console.error("Error creating session:", error);
        return false;
    }
}

export async function clearSession() {
    try {
        const cookieStore = await cookies();
        cookieStore.delete('session_token');

        return true;
    } catch (error) {
        console.error("Error deleting session:", error);
        return false;
    }
}