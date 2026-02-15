import { Suspense } from 'react';
import AuthPage from "../auth";

export default function Page() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <AuthPage />
        </Suspense>
    );
}

