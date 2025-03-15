import { getCurrentUser } from "@/app/lib/users";

export default async function Page(){
    const user = await getCurrentUser();
    return <div>{user}</div>;
}