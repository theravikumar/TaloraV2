import { Suspense } from 'react';
import JobsPage from "../jobs";

export default function Page() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <JobsPage />
        </Suspense>
    );
}

