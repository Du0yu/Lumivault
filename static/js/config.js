// Docker路径设置
function setDockerPath() {
    const pathInput = document.getElementById('base_path');
    if (pathInput) {
        pathInput.value = '/app/media';
        pathInput.focus();
        
        // 添加视觉反馈
        pathInput.style.borderColor = '#00b4d8';
        pathInput.style.backgroundColor = 'rgba(0, 180, 216, 0.1)';
        
        // 2秒后恢复样式
        setTimeout(() => {
            pathInput.style.borderColor = '';
            pathInput.style.backgroundColor = '';
        }, 2000);
        
        // 显示提示信息
        showMessage('已设置为Docker容器路径: /app/media', 'info');
    }
}

// 重载媒体库
function reloadLibrary() {
    if (confirm('确定要重载媒体库吗？这将清除所有缓存并重新扫描媒体文件。')) {
        showMessage('正在重载媒体库...', 'info');
        
        fetch('/reload_library', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showMessage(data.message, 'success');
            } else {
                showMessage(data.message, 'error');
            }
        })
        .catch(error => {
            showMessage('重载失败: ' + error.message, 'error');
        });
    }
}

// 重启服务器
function restartServer() {
    if (confirm('确定要重启服务器吗？页面将会短暂断开连接。')) {
        showMessage('正在重启服务器...', 'info');
        
        fetch('/restart_server', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showMessage(data.message, 'success');
                // 3秒后刷新页面
                setTimeout(() => {
                    window.location.reload();
                }, 3000);
            } else {
                showMessage(data.message, 'error');
            }
        })
        .catch(error => {
            showMessage('重启请求已发送，页面将自动刷新...', 'info');
            // 5秒后尝试刷新页面
            setTimeout(() => {
                window.location.reload();
            }, 5000);
        });
    }
}

// 切换隐藏空文件夹设置
function toggleHideEmptyFolders(checkbox) {
    const formData = new FormData();
    formData.append('base_path', document.getElementById('base_path').value);
    formData.append('hide_empty_folders', checkbox.checked ? 'on' : '');
    
    fetch('/config', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            showMessage(checkbox.checked ? '已启用隐藏空文件夹' : '已禁用隐藏空文件夹', 'success');
        } else {
            showMessage('设置保存失败', 'error');
            // 如果失败，恢复开关状态
            checkbox.checked = !checkbox.checked;
        }
    })
    .catch(error => {
        showMessage('设置保存失败: ' + error.message, 'error');
        // 如果失败，恢复开关状态
        checkbox.checked = !checkbox.checked;
    });
}

// 显示消息提示
function showMessage(message, type = 'info') {
    // 移除已存在的消息
    const existingMessage = document.querySelector('.temp-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'temp-message';
    messageDiv.textContent = message;
    
    // 根据类型设置样式
    const colors = {
        'success': { bg: '#d4edda', border: '#c3e6cb', text: '#155724' },
        'error': { bg: '#f8d7da', border: '#f5c6cb', text: '#721c24' },
        'info': { bg: '#d1ecf1', border: '#bee5eb', text: '#0c5460' }
    };
    
    const color = colors[type] || colors['info'];
    
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${color.bg};
        border: 1px solid ${color.border};
        color: ${color.text};
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 10000;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    document.body.appendChild(messageDiv);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, 3000);
}
