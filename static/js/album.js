// 按比例分组图片
function groupImagesByRatio() {
    document.querySelectorAll('.media-list').forEach(function(mediaList) {
        if (!mediaList.querySelector('.media-item img')) return; // 跳过视频列表
        
        const items = Array.from(mediaList.querySelectorAll('.media-item'));
        const ratioGroups = {};
        
        // 按比例分组
        items.forEach(function(item) {
            const ratioClass = item.className.match(/ratio-[\w-]+/);
            if (ratioClass) {
                const ratio = ratioClass[0];
                if (!ratioGroups[ratio]) {
                    ratioGroups[ratio] = [];
                }
                ratioGroups[ratio].push(item);
            }
        });
        
        // 清空原容器
        mediaList.innerHTML = '';
        
        // 重新添加分组后的元素
        Object.keys(ratioGroups).forEach(function(ratio, index) {
            if (index > 0) {
                // 添加分隔线
                const separator = document.createElement('div');
                separator.className = 'ratio-separator';
                mediaList.appendChild(separator);
            }
            
            const group = document.createElement('div');
            group.className = 'ratio-group';
            ratioGroups[ratio].forEach(function(item) {
                group.appendChild(item);
            });
            mediaList.appendChild(group);
        });
    });
}

// 收集所有图片信息
const allImages = {};
document.querySelectorAll('.category').forEach(function(categoryDiv) {
    const category = categoryDiv.querySelector('h2').textContent.trim();
    const imgs = Array.from(categoryDiv.querySelectorAll('.zoomable-image'));
    allImages[category] = imgs;
});

let currentZoom = {
    img: null,
    category: null,
    index: null
};

function showZoomNavBtns(show) {
    let nav = document.querySelector('.zoom-nav-btns');
    let closeBtn = document.querySelector('.zoom-close-btn');
    if (nav) nav.style.display = show ? 'flex' : 'none';
    if (closeBtn) closeBtn.style.display = show ? 'flex' : 'none';
}

function updateZoomedImage(category, idx) {
    const imgs = allImages[category];
    if (!imgs || idx < 0 || idx >= imgs.length) return;
    const src = imgs[idx].src;
    const zoomed = document.querySelector('.zoomed');
    if (zoomed) {
        zoomed.src = src;
        currentZoom.category = category;
        currentZoom.index = idx;
    }
}

function closeZoom() {
    let zoomed = document.querySelector('.zoomed');
    if (zoomed) zoomed.classList.remove('zoomed');
    let overlay = document.querySelector('.zoom-overlay');
    if (overlay) overlay.remove();
    showZoomNavBtns(false);
    // 移除关闭按钮
    let closeBtn = document.querySelector('.zoom-close-btn');
    if (closeBtn) closeBtn.style.display = 'none';
    document.body.style.overflow = '';
    currentZoom.img = null;
    currentZoom.category = null;
    currentZoom.index = null;
}

// 创建导航按钮和关闭按钮
function createZoomNavBtns() {
    if (!document.querySelector('.zoom-nav-btns')) {
        const nav = document.createElement('div');
        nav.className = 'zoom-nav-btns';
        nav.innerHTML = `
            <button class="zoom-nav-btn" id="zoomPrevBtn" title="上一张">&#8592;</button>
            <button class="zoom-nav-btn" id="zoomNextBtn" title="下一张">&#8594;</button>
        `;
        document.body.appendChild(nav);
        nav.style.display = 'none';

        nav.querySelector('#zoomPrevBtn').onclick = function(e) {
            e.stopPropagation();
            if (currentZoom.category && currentZoom.index > 0) {
                updateZoomedImage(currentZoom.category, currentZoom.index - 1);
            }
        };
        nav.querySelector('#zoomNextBtn').onclick = function(e) {
            e.stopPropagation();
            const imgs = allImages[currentZoom.category];
            if (imgs && currentZoom.index < imgs.length - 1) {
                updateZoomedImage(currentZoom.category, currentZoom.index + 1);
            }
        };
    }
    if (!document.querySelector('.zoom-close-btn')) {
        const closeBtn = document.createElement('button');
        closeBtn.className = 'zoom-close-btn';
        closeBtn.title = '关闭';
        closeBtn.innerHTML = '&times;';
        closeBtn.onclick = function(e) {
            e.stopPropagation();
            closeZoom();
        };
        closeBtn.style.display = 'none';
        document.body.appendChild(closeBtn);
    }
}

// 放大图片功能（增强，支持滑动）
function setupImageZoom() {
    document.querySelectorAll('.zoomable-image').forEach(function(img) {
        img.addEventListener('click', function(e) {
            e.preventDefault();
            closeZoom();
            // 创建放大用的大图
            const zoomedImg = img.cloneNode(true);
            zoomedImg.classList.add('zoomed');
            // 移除已存在的放大图
            document.querySelectorAll('.zoomed').forEach(function(z) {
                if (z !== zoomedImg) z.remove();
            });
            document.body.appendChild(zoomedImg);
            document.body.style.overflow = 'hidden';
            // 添加遮罩
            let overlay = document.createElement('div');
            overlay.className = 'zoom-overlay';
            overlay.onclick = closeZoom;
            document.body.appendChild(overlay);

            // 记录当前
            const category = img.getAttribute('data-category');
            const index = parseInt(img.getAttribute('data-index'));
            currentZoom.img = zoomedImg;
            currentZoom.category = category;
            currentZoom.index = index;

            showZoomNavBtns(true);

            document.onkeydown = function(ev) {
                if (!document.querySelector('.zoomed')) return;
                if (ev.key === 'ArrowLeft') {
                    if (currentZoom.category && currentZoom.index > 0) {
                        updateZoomedImage(currentZoom.category, currentZoom.index - 1);
                    }
                } else if (ev.key === 'ArrowRight') {
                    const imgs = allImages[currentZoom.category];
                    if (imgs && currentZoom.index < imgs.length - 1) {
                        updateZoomedImage(currentZoom.category, currentZoom.index + 1);
                    }
                } else if (ev.key === 'Escape') {
                    closeZoom();
                }
            };

            // 移动端滑动支持
            let startX = null;
            let startY = null;
            let moved = false;
            zoomedImg.addEventListener('touchstart', function(ev) {
                if (ev.touches.length === 1) {
                    startX = ev.touches[0].clientX;
                    startY = ev.touches[0].clientY;
                    moved = false;
                }
            }, {passive: true});
            zoomedImg.addEventListener('touchmove', function(ev) {
                moved = true;
            }, {passive: true});
            zoomedImg.addEventListener('touchend', function(ev) {
                if (!moved || startX === null) return;
                let endX = ev.changedTouches[0].clientX;
                let endY = ev.changedTouches[0].clientY;
                let dx = endX - startX;
                let dy = endY - startY;
                if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) {
                    // 左右滑动
                    if (dx < 0) {
                        const imgs = allImages[currentZoom.category];
                        if (imgs && currentZoom.index < imgs.length - 1) {
                            updateZoomedImage(currentZoom.category, currentZoom.index + 1);
                        }
                    } else {
                        if (currentZoom.category && currentZoom.index > 0) {
                            updateZoomedImage(currentZoom.category, currentZoom.index - 1);
                        }
                    }
                }
                startX = null;
                startY = null;
                moved = false;
            }, {passive: true});
        });
    });

    // 点击放大图片时禁止链接跳转
    document.querySelectorAll('.image-link').forEach(function(link) {
        link.addEventListener('click', function(e) {
            let img = link.querySelector('.zoomable-image');
            if (img && img.classList.contains('zoomed')) {
                e.preventDefault();
            }
        });
    });

    // 关闭放大时移除键盘事件
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('zoom-overlay')) {
            document.onkeydown = null;
        }
    });
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // Group media items by aspect ratio
    function groupMediaByRatio() {
        const mediaLists = document.querySelectorAll('.media-list');
        
        mediaLists.forEach(function(mediaList) {
            const mediaItems = Array.from(mediaList.children);
            const ratioGroups = {};
            
            // Group items by ratio class
            mediaItems.forEach(function(item) {
                const ratioClass = Array.from(item.classList).find(cls => cls.startsWith('ratio-'));
                if (ratioClass) {
                    if (!ratioGroups[ratioClass]) {
                        ratioGroups[ratioClass] = [];
                    }
                    ratioGroups[ratioClass].push(item);
                }
            });
            
            // Clear the original list
            mediaList.innerHTML = '';
            
            // Create ratio groups
            Object.keys(ratioGroups).forEach(function(ratioClass, index) {
                const group = document.createElement('div');
                group.className = 'ratio-group';
                
                ratioGroups[ratioClass].forEach(function(item) {
                    group.appendChild(item);
                });
                
                mediaList.appendChild(group);
                
                // Add separator between groups (except for the last one)
                if (index < Object.keys(ratioGroups).length - 1) {
                    const separator = document.createElement('div');
                    separator.className = 'ratio-separator';
                    mediaList.appendChild(separator);
                }
            });
        });
    }
    
    // Initialize grouping
    groupMediaByRatio();

    createZoomNavBtns();
    setupImageZoom();
});
