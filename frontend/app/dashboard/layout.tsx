import SideNav from '@/app/ui/dashboard/sidenav';
import { isLoggedIn } from '../lib/session';
import { redirect } from 'next/navigation';

// 1. Import the SideNav componenet
// 2. your current page content is passed as children to the Layout component
export default async function Layout({ children }: { children: React.ReactNode }) {
    const signedIn = await isLoggedIn();
    if (!signedIn) redirect('/login');

    return (
        <div className="flex h-screen flex-col md:flex-row md:overflow-hidden">
        <div className="w-full flex-none md:w-64">
            <SideNav />
        </div>
        <div className="flex-grow p-6 md:overflow-y-auto md:p-12">{children}</div>
        </div>
    );
}