(function () {
    function getStored() {
        try {
            return localStorage.getItem('theme');
        } catch (e) {
            return null;
        }
    }

    function setStored(value) {
        try {
            localStorage.setItem('theme', value);
        } catch (e) {
            /* localStorage unavailable (private mode, etc.) — theme just won't persist */
        }
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        var btn = document.getElementById('theme-toggle');
        if (btn) {
            btn.setAttribute('aria-pressed', theme === 'light' ? 'true' : 'false');
            btn.setAttribute('aria-label', theme === 'light' ? 'Ganti ke mode gelap' : 'Ganti ke mode terang');
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        applyTheme(document.documentElement.getAttribute('data-theme') || 'dark');

        var btn = document.getElementById('theme-toggle');
        if (btn) {
            btn.addEventListener('click', function () {
                var next = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
                setStored(next);
                applyTheme(next);
            });
        }
    });
})();
