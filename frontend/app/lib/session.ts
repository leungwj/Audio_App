import 'server-only'
import { cookies } from 'next/headers'
 
export async function createSession(token: string) {
  const expiresAt = new Date(Date.now() + 30 * 60 * 1000)
  const session = await encrypt({ userId, expiresAt })
  const cookieStore = await cookies()
 
  cookieStore.set('session', session, {
    httpOnly: true,
    secure: true,
    expires: expiresAt,
    sameSite: 'lax',
    path: '/',
  })
}