/**
 * Main Application Logic
 */

const App = {
    init: function () {
        this.renderHeader();
        this.highlightCurrentPage();
    },

    renderHeader: function () {
        const headerEl = document.getElementById('app-header');
        if (!headerEl) return;

        const user = Auth.getUser();
        if (!user) return; // Don't render header on login page properly if wrapped

        const isAdmin = user.role === 'admin';

        headerEl.innerHTML = `
            <nav class="navbar">
                <div class="container nav-container">
                    <a href="index.html" class="nav-brand">HI 면접 MASTER</a>
                    
                    <ul class="nav-menu">
                        <li><a href="index.html" class="nav-link" data-page="index.html">대시보드</a></li>
                        <li><a href="videos.html" class="nav-link" data-page="videos.html">강의 목록</a></li>
                        <li><a href="learning.html" class="nav-link" data-page="learning.html">나의 학습</a></li>
                        ${isAdmin ? '<li><a href="admin.html" class="nav-link" data-page="admin.html">관리자</a></li>' : ''}
                    </ul>

                    <div class="nav-profile" onclick="App.toggleProfileMenu()">
                        <div class="avatar">
                            <img src="${user.avatar}" alt="${user.name}" style="border-radius: 50%; width: 100%; height: 100%;">
                        </div>
                        <span style="font-weight: 500; font-size: 0.9rem;">${user.name}</span>
                        <!-- Simple dropdown -->
                        <div id="profile-menu" class="card hidden" style="position: absolute; top: 60px; right: 0; width: 150px; padding: 0.5rem; z-index: 200;">
                            <a href="#" onclick="Auth.logout()" style="display: block; padding: 0.5rem; color: var(--danger-color);">Logout</a>
                        </div>
                    </div>
                </div>
            </nav>
        `;
    },

    toggleProfileMenu: function () {
        const menu = document.getElementById('profile-menu');
        if (menu) menu.classList.toggle('hidden');
    },

    highlightCurrentPage: function () {
        const path = window.location.pathname;
        const page = path.split('/').pop() || 'index.html';
        const links = document.querySelectorAll('.nav-link');
        links.forEach(link => {
            if (link.getAttribute('data-page') === page) {
                link.classList.add('active');
            }
        });
    },

    // Utility: Format seconds to MM:SS
    formatTime: function (seconds) {
        if (!seconds) return '0:00';
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60);
        return `${m}:${s.toString().padStart(2, '0')}`;
    }
};

// Auto-init specific components if they exist
document.addEventListener('DOMContentLoaded', () => {
    // Only init app if not on login page (or handle strictly)
    if (!window.location.pathname.includes('login.html')) {
        App.init();
    }
});
