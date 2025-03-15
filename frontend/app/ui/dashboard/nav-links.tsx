"use client";
// this is required because usePathname() is a React hook
// hence, we need to turn this into a client component

import {
  UserGroupIcon,
  HomeIcon,
  MusicalNoteIcon
} from '@heroicons/react/24/outline';
import Link from 'next/link';
import { usePathname } from 'next/navigation'; // determine the current path
import clsx from 'clsx'; // apply different class to current path link component

// Map of links to display in the side navigation.
// Depending on the size of the application, this would be stored in a database.
const links = [
  { name: 'Home', href: '/dashboard', icon: HomeIcon },
  {
    name: 'Audio Files',
    href: '/dashboard/audio_files',
    icon: MusicalNoteIcon,
  },
  { name: 'Users', href: '/dashboard/users', icon: UserGroupIcon },
];

export default function NavLinks() {
  const pathname = usePathname();
  return (
    // for each element in link, create a Link component
    <>
      {links.map((link) => {
        const LinkIcon = link.icon;
        return (
          <Link
            key={link.name}
            href={link.href}
            className={clsx(
              "flex h-[48px] grow items-center justify-center gap-2 rounded-md bg-gray-50 p-3 text-sm font-medium hover:bg-sky-100 hover:text-blue-600 md:flex-none md:justify-start md:p-2 md:px-3",
              {
                // if the current path is the same as the link, apply the following additional classes
                'bg-sky-100 text-blue-600': pathname === link.href,
              }
            )}
          >
            <LinkIcon className="w-6" />
            <p className="hidden md:block">{link.name}</p>
          </Link>
        );
      })}
    </>
  );
}
