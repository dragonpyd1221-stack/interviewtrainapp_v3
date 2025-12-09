const Auth = {
    async login(email, password) {
        try {
            const res = await fetch('http://localhost:8000/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (!res.ok) {
                const err = await res.json();
                return { success: false, message: err.detail || '로그인 실패' };
            }

            const data = await res.json();
            localStorage.setItem('user_session', JSON.stringify(data));
            return { success: true };
        } catch (e) {
            console.error('Login error', e);
            return { success: false, message: '서버 연결 오류' };
        }
    },

    logout() {
        localStorage.removeItem('user_session');
        window.location.href = 'login.html';
    },

    getUser() {
        const json = localStorage.getItem('user_session');
        return json ? JSON.parse(json) : null;
    },

    requireAuth() {
        const user = this.getUser();
        if (!user) {
            window.location.href = 'login.html';
            return null;
        }
        return user;
    },

    requireAdmin() {
        const user = this.requireAuth();
        if (user && user.role !== 'admin') {
            alert('관리자 권한이 필요합니다.');
            window.location.href = 'index.html';
            return null;
        }
        return user;
    }
};
