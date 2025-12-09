const API_BASE_URL = 'http://localhost:8000/api';

const DataManager = {
    // --- Videos ---
    async getVideos(category = null) {
        try {
            let url = `${API_BASE_URL}/videos`;
            if (category && category !== 'all') {
                url += `?category=${category}`;
            }
            const res = await fetch(url); // CORS must be enabled on backend
            if (!res.ok) throw new Error('Failed to fetch videos');
            return await res.json();
        } catch (e) {
            console.error(e);
            return [];
        }
    },

    async getVideoById(id) {
        try {
            const res = await fetch(`${API_BASE_URL}/videos/${id}`);
            if (!res.ok) return null;
            return await res.json();
        } catch (e) {
            return null;
        }
    },

    async getCategories() {
        // Hardcoded categories for UI consistency, or fetch from DB if we had a categories table
        return [
            { id: 'all', name: '전체 보기' },
            { id: 'required', name: '필수 교육' },
            { id: 'optional', name: '선택 교육' }
        ];
    },

    async addVideo(formData) {
        // formData must contain: title, category, file (optional), etc.
        const res = await fetch(`${API_BASE_URL}/videos`, {
            method: 'POST',
            body: formData, // No Content-Type header when sending FormData; browser sets it
        });
        if (!res.ok) throw new Error('Upload failed');
        return await res.json();
    },

    async deleteVideo(id) {
        await fetch(`${API_BASE_URL}/videos/${id}`, { method: 'DELETE' });
    },

    // --- Progress ---
    async getProgress() {
        // Get current user email from Auth
        const user = Auth.getUser();
        if (!user) return {};

        try {
            const res = await fetch(`${API_BASE_URL}/progress/${user.email}`);
            return await res.json();
        } catch (e) {
            console.error(e);
            return {};
        }
    },

    async getVideoProgress(videoId) {
        const allProgress = await this.getProgress();
        return allProgress[videoId] || { timestamp: 0, status: 'unwatched' };
    },

    async saveProgress(videoId, data) {
        const user = Auth.getUser();
        if (!user) return;

        const payload = {
            email: user.email,
            video_id: videoId,
            timestamp: data.timestamp,
            status: data.status
        };

        await fetch(`${API_BASE_URL}/progress`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    }
};
