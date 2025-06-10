// 重载媒体库
function reloadLibrary() {
    if (confirm('确定要重载媒体库吗？这将刷新所有媒体文件和缩略图缓存。')) {
        fetch('/reload_library', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        }).then(response => {
            if (response.ok) {
                alert('媒体库重载成功！');
                location.reload();
            } else {
                alert('重载失败，请检查控制台错误信息。');
            }
        }).catch(error => {
            alert('重载失败：' + error.message);
        });
    }
}

// 重启服务器
function restartServer() {
    if (confirm('确定要重启服务器吗？页面将自动刷新。')) {
        const restartBtn = event.target;
        const originalText = restartBtn.textContent;
        
        // 禁用按钮并显示加载状态
        restartBtn.disabled = true;
        restartBtn.textContent = '重启中...';
        
        fetch('/restart_server', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        }).then(response => {
            if (response.ok) {
                alert('服务器正在重启，页面将在3秒后刷新...');
                // 等待3秒后刷新页面
                setTimeout(() => {
                    location.reload();
                }, 3000);
            } else {
                throw new Error('重启请求失败');
            }
        }).catch(error => {
            // 重启时连接可能会断开，这是正常的
            console.log('重启请求:', error.message);
            alert('服务器正在重启，页面将在5秒后刷新...');
            
            // 恢复按钮状态
            restartBtn.disabled = false;
            restartBtn.textContent = originalText;
            
            // 尝试重新连接
            let retryCount = 0;
            const maxRetries = 10;
            const retryInterval = 1000; // 1秒
            
            const checkServer = () => {
                retryCount++;
                fetch('/', { method: 'HEAD' })
                    .then(response => {
                        if (response.ok) {
                            location.reload();
                        } else if (retryCount < maxRetries) {
                            setTimeout(checkServer, retryInterval);
                        } else {
                            alert('服务器重启完成，请手动刷新页面');
                        }
                    })
                    .catch(() => {
                        if (retryCount < maxRetries) {
                            setTimeout(checkServer, retryInterval);
                        } else {
                            alert('服务器重启完成，请手动刷新页面');
                        }
                    });
            };
            
            // 等待3秒后开始检查服务器状态
            setTimeout(checkServer, 3000);
        });
    }
}
