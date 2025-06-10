// 主题切换功能
function initTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    document.documentElement.setAttribute('data-theme', currentTheme);
    themeToggle.textContent = currentTheme === 'dark' ? '☀️' : '🌙';
    
    themeToggle.addEventListener('click', function() {
        const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        themeToggle.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    });
}

// 移动端侧边菜单
function setupSideMenu() {
    var menuIcon = document.getElementById('navbarMenuIcon');
    var sideMenu = document.getElementById('sideMenu');
    var sideMenuClose = document.getElementById('sideMenuClose');
    
    function openMenu() {
        sideMenu.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
    
    function closeMenu() {
        sideMenu.classList.remove('open');
        document.body.style.overflow = '';
    }
    
    if (menuIcon && sideMenu && sideMenuClose) {
        menuIcon.addEventListener('click', openMenu);
        sideMenuClose.addEventListener('click', closeMenu);
        // 点击菜单外部关闭
        document.addEventListener('click', function(e) {
            if (sideMenu.classList.contains('open') && !sideMenu.contains(e.target) && e.target !== menuIcon) {
                closeMenu();
            }
        });
    }
}

// 标签页切换功能
function setupTabs() {
    document.querySelectorAll('.tab-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var targetTabId = this.getAttribute('data-tab');
            var categoryDiv = this.closest('.category');
            
            // 移除同组标签的active状态
            categoryDiv.querySelectorAll('.tab-btn').forEach(function(b) {
                b.classList.remove('active');
            });
            categoryDiv.querySelectorAll('.tab-content').forEach(function(content) {
                content.classList.remove('active');
            });
            
            // 激活当前标签
            this.classList.add('active');
            document.getElementById(targetTabId).classList.add('active');
        });
    });
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    setupSideMenu();
    setupTabs();
});
